from copy import deepcopy
import math

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from estado_duelo import EstadoDuelo
from heuristica import avaliar_estado
from instancias import legolas, mago_negro


# ─────────────────────────────────────────
#  Lógica do duelo (igual ao main.py)
# ─────────────────────────────────────────

def personagem_ativo(estado: EstadoDuelo):
    return estado.personagem_1 if estado.turno_do_p1 else estado.personagem_2


def personagem_passivo(estado: EstadoDuelo):
    return estado.personagem_2 if estado.turno_do_p1 else estado.personagem_1


def duelo_encerrado(estado: EstadoDuelo) -> bool:
    return estado.personagem_1.vida <= 0 or estado.personagem_2.vida <= 0


def vencedor(estado: EstadoDuelo):
    if estado.personagem_2.vida <= 0:
        return "p1"
    if estado.personagem_1.vida <= 0:
        return "p2"
    return None


def gera_acoes(estado: EstadoDuelo) -> list:
    ativo = personagem_ativo(estado)
    acoes_disponiveis = []

    if ativo.arma:
        acoes_disponiveis.append({"tipo": "atacar"})

    for magia in ativo.magias:
        if magia.custo_mana <= ativo.mana:
            acoes_disponiveis.append({"tipo": "magia", "nome_magia": magia.nome})

    return acoes_disponiveis


def aplica_acao(estado: EstadoDuelo, acao: dict) -> tuple[EstadoDuelo, str]:
    """Aplica a ação e retorna (novo_estado, linha_de_log)."""
    novo = deepcopy(estado)
    ativo = personagem_ativo(novo)
    alvo = personagem_passivo(novo)
    linha_log = ""

    if acao["tipo"] == "atacar":
        dano = ativo.arma.dano if ativo.arma else 0
        alvo.vida -= dano
        alvo.vida = max(0, alvo.vida)
        linha_log = f"{ativo.nome} atacou com {ativo.arma.nome} e causou {dano} de dano em {alvo.nome}."

    elif acao["tipo"] == "magia":
        magia_escolhida = None
        for magia in ativo.magias:
            if magia.nome == acao["nome_magia"]:
                magia_escolhida = magia
                break

        if magia_escolhida is None:
            raise ValueError(f"Magia '{acao['nome_magia']}' não encontrada")

        ativo.mana -= magia_escolhida.custo_mana
        ativo.mana = max(0, ativo.mana)
        alvo.vida -= magia_escolhida.dano
        alvo.vida = max(0, alvo.vida)

        if magia_escolhida.dano < 0:
            linha_log = f"{ativo.nome} conjurou {magia_escolhida.nome} e recuperou {-magia_escolhida.dano} de vida."
        else:
            linha_log = f"{ativo.nome} conjurou {magia_escolhida.nome} e causou {magia_escolhida.dano} de dano em {alvo.nome}."

    novo.turno_do_p1 = not novo.turno_do_p1
    return novo, linha_log


def negamax(estado: EstadoDuelo, profundidade: int, alfa: float, beta: float) -> float:
    if duelo_encerrado(estado) or profundidade == 0:
        valor = avaliar_estado(estado)
        return valor if estado.turno_do_p1 else -valor

    melhor_valor = -math.inf

    for acao in gera_acoes(estado):
        novo_estado, _ = aplica_acao(estado, acao)
        valor = -negamax(novo_estado, profundidade - 1, -beta, -alfa)

        if valor > melhor_valor:
            melhor_valor = valor
        if valor > alfa:
            alfa = valor
        if alfa >= beta:
            break

    return melhor_valor


def escolher_melhor_acao(estado: EstadoDuelo, profundidade: int = 4) -> dict:
    melhor_acao = None
    melhor_valor = -math.inf

    for acao in gera_acoes(estado):
        novo_estado, _ = aplica_acao(estado, acao)
        valor = -negamax(novo_estado, profundidade - 1, -math.inf, math.inf)

        if valor > melhor_valor:
            melhor_valor = valor
            melhor_acao = acao

    return melhor_acao


# ─────────────────────────────────────────
#  Estado da partida (em memória, 1 partida global)
# ─────────────────────────────────────────

PROFUNDIDADE_IA = 4

# Guardamos vida_max/mana_max separadamente porque a dataclass Personagem
# só tem "vida"/"mana" atuais.
def novo_jogo():
    p1 = deepcopy(legolas)
    p2 = deepcopy(mago_negro)
    estado = EstadoDuelo(personagem_1=p1, personagem_2=p2, turno_do_p1=True)
    return {
        "estado": estado,
        "vida_max_p1": p1.vida,
        "mana_max_p1": p1.mana,
        "vida_max_p2": p2.vida,
        "mana_max_p2": p2.mana,
        "log": [],
        "encerrado": False,
        "vencedor": None,
    }


jogo = novo_jogo()


# ─────────────────────────────────────────
#  Serialização para o formato esperado pelo frontend
# ─────────────────────────────────────────

def acoes_para_frontend(estado: EstadoDuelo) -> list:
    ativo = personagem_ativo(estado)
    acoes = []

    if ativo.arma:
        acoes.append({
            "tipo": "atacar",
            "id": "atacar",
            "label": f"Atacar ({ativo.arma.nome})",
            "disponivel": True,
        })

    for magia in ativo.magias:
        disponivel = magia.custo_mana <= ativo.mana
        acoes.append({
            "tipo": "magia",
            "id": magia.nome,
            "label": f"{magia.nome} ({magia.custo_mana} mana)",
            "disponivel": disponivel,
        })

    return acoes


def estado_para_frontend() -> dict:
    estado = jogo["estado"]
    p1, p2 = estado.personagem_1, estado.personagem_2

    return {
        "jogador": {
            "nome": p1.nome,
            "vida": p1.vida,
            "vida_max": jogo["vida_max_p1"],
            "mana": p1.mana,
            "mana_max": jogo["mana_max_p1"],
        },
        "ia": {
            "nome": p2.nome,
            "vida": p2.vida,
            "vida_max": jogo["vida_max_p2"],
            "mana": p2.mana,
            "mana_max": jogo["mana_max_p2"],
        },
        "turno": "jogador" if (estado.turno_do_p1 and not jogo["encerrado"]) else "ia",
        "encerrado": jogo["encerrado"],
        "vencedor": jogo["vencedor"],
        "log": jogo["log"],
        # Só manda ações se for a vez do jogador e o jogo não acabou
        "acoes": acoes_para_frontend(estado) if (estado.turno_do_p1 and not jogo["encerrado"]) else [],
    }


def checar_fim_de_jogo():
    if duelo_encerrado(jogo["estado"]):
        jogo["encerrado"] = True
        ganhador = vencedor(jogo["estado"])
        jogo["vencedor"] = "jogador" if ganhador == "p1" else "ia"


def turno_da_ia():
    """Roda o turno da IA automaticamente após a jogada do jogador."""
    while not jogo["encerrado"] and not jogo["estado"].turno_do_p1:
        acao = escolher_melhor_acao(jogo["estado"], profundidade=PROFUNDIDADE_IA)
        novo_estado, linha_log = aplica_acao(jogo["estado"], acao)
        jogo["estado"] = novo_estado
        jogo["log"].append(linha_log)
        checar_fim_de_jogo()


# ─────────────────────────────────────────
#  API
# ─────────────────────────────────────────

class AcaoRequest(BaseModel):
    tipo: str
    id: str


app = FastAPI(title="RPG de Duelo")


@app.get("/")
def raiz():
    return FileResponse("templates/index.html")


@app.get("/estado")
def get_estado():
    return estado_para_frontend()


@app.post("/acao")
def post_acao(acao_req: AcaoRequest):
    if jogo["encerrado"] or not jogo["estado"].turno_do_p1:
        return estado_para_frontend()

    if acao_req.tipo == "atacar":
        acao = {"tipo": "atacar"}
    else:
        acao = {"tipo": "magia", "nome_magia": acao_req.id}

    novo_estado, linha_log = aplica_acao(jogo["estado"], acao)
    jogo["estado"] = novo_estado
    jogo["log"].append(linha_log)
    checar_fim_de_jogo()

    turno_da_ia()

    return estado_para_frontend()


@app.post("/reiniciar")
def post_reiniciar():
    global jogo
    jogo = novo_jogo()
    return estado_para_frontend()


app.mount("/templates", StaticFiles(directory="templates"), name="templates")