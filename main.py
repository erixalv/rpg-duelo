from copy import deepcopy
import math

from estado_duelo import EstadoDuelo
from heuristica import avaliar_estado
from instancias import arthur, mago_negro


# ─────────────────────────────────────────
#  Funções auxiliares
#  (o EstadoDuelo real não tem esses métodos, então ficam aqui fora)
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


# ─────────────────────────────────────────
#  Geração e aplicação de ações
# ─────────────────────────────────────────

def gera_acoes(estado: EstadoDuelo) -> list:
    ativo = personagem_ativo(estado)
    acoes_disponiveis = []

    if ativo.arma:
        acoes_disponiveis.append({"tipo": "atacar"})

    for magia in ativo.magias:
        if magia.custo_mana <= ativo.mana:
            acoes_disponiveis.append({"tipo": "magia", "nome_magia": magia.nome})

    return acoes_disponiveis


def aplica_acao(estado: EstadoDuelo, acao: dict) -> EstadoDuelo:
    novo = deepcopy(estado)
    ativo = personagem_ativo(novo)
    alvo = personagem_passivo(novo)

    if acao["tipo"] == "atacar":
        dano = ativo.arma.dano if ativo.arma else 0
        alvo.vida -= dano
        alvo.vida = max(0, alvo.vida)

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

        if magia_escolhida.dano < 0:
            ativo.vida -= magia_escolhida.dano
        else:
            alvo.vida -= magia_escolhida.dano
            alvo.vida = max(0, alvo.vida)

    novo.turno_do_p1 = not novo.turno_do_p1
    return novo


# ─────────────────────────────────────────
#  Negamax com poda alfa-beta
# ─────────────────────────────────────────

def negamax(estado: EstadoDuelo, profundidade: int, alfa: float, beta: float) -> float:
    if duelo_encerrado(estado) or profundidade == 0:
        valor = avaliar_estado(estado)
        # avaliar_estado é sempre do ponto de vista de p1.
        # Se quem está "na vez" agora é p2, invertemos o sinal
        # para manter a convenção do Negamax (positivo = bom pra quem joga agora).
        return valor if estado.turno_do_p1 else -valor

    melhor_valor = -math.inf

    for acao in gera_acoes(estado):
        novo_estado = aplica_acao(estado, acao)
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
        novo_estado = aplica_acao(estado, acao)
        valor = -negamax(novo_estado, profundidade - 1, -math.inf, math.inf)

        if valor > melhor_valor:
            melhor_valor = valor
            melhor_acao = acao

    return melhor_acao


# ─────────────────────────────────────────
#  Interface de texto / descrição de ações
# ─────────────────────────────────────────

def descreve_acao(personagem, acao: dict) -> str:
    if acao["tipo"] == "atacar":
        return f"Atacar com {personagem.arma.nome} ({personagem.arma.dano} de dano)"
    nome = acao["nome_magia"]
    magia = next(m for m in personagem.magias if m.nome == nome)
    tipo_efeito = "cura" if magia.dano < 0 else "dano"
    return f"Conjurar {magia.nome} (custo {magia.custo_mana} mana, {abs(magia.dano)} de {tipo_efeito})"


def mostra_status(estado: EstadoDuelo):
    p1, p2 = estado.personagem_1, estado.personagem_2
    print("-" * 50)
    print(f"{p1.nome:25} | Vida: {p1.vida:4} | Mana: {p1.mana:4}")
    print(f"{p2.nome:25} | Vida: {p2.vida:4} | Mana: {p2.mana:4}")
    print("-" * 50)


# ─────────────────────────────────────────
#  Loop principal do duelo interativo
# ─────────────────────────────────────────

def duelo_interativo(estado: EstadoDuelo, profundidade_ia: int = 4):
    print("\n=== DUELO INICIADO ===")
    print(f"Você controla: {estado.personagem_1.nome}")
    print(f"A IA controla: {estado.personagem_2.nome}\n")

    quem = "Você" if estado.turno_do_p1 else "IA"
    print(f"🎲 Sorteio: {quem} ataca primeiro!\n")

    while not duelo_encerrado(estado):
        mostra_status(estado)

        if estado.turno_do_p1:
            ativo = personagem_ativo(estado)
            acoes = gera_acoes(estado)

            print(f"\nTurno de {ativo.nome} (você):")
            for i, acao in enumerate(acoes, start=1):
                print(f"  {i}. {descreve_acao(ativo, acao)}")

            escolha = None
            while escolha is None:
                bruto = input("Escolha uma ação: ").strip()
                if bruto.isdigit() and 1 <= int(bruto) <= len(acoes):
                    escolha = acoes[int(bruto) - 1]
                else:
                    print("Opção inválida, tente novamente.")

            estado = aplica_acao(estado, escolha)

        else:
            ativo = personagem_ativo(estado)
            print(f"\nTurno de {ativo.nome} (IA)...")
            acao = escolher_melhor_acao(estado, profundidade=profundidade_ia)
            print(f"IA escolheu: {descreve_acao(ativo, acao)}")
            estado = aplica_acao(estado, acao)

    mostra_status(estado)
    ganhador = vencedor(estado)
    nome_vencedor = estado.personagem_1.nome if ganhador == "p1" else estado.personagem_2.nome
    print(f"\n*** {nome_vencedor} venceu o duelo! ***")


if __name__ == "__main__":
    import random
    estado_inicial = EstadoDuelo(
        personagem_1=deepcopy(arthur),
        personagem_2=deepcopy(mago_negro),
        turno_do_p1=random.choice([True, False]),
    )
    duelo_interativo(estado_inicial, profundidade_ia=4)