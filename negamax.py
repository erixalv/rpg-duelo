from estado_duelo import EstadoDuelo
from copy import deepcopy
from heuristica import heuristica
import math

def gera_acoes(estado : EstadoDuelo) -> list:
    personagem = estado.personagem_ativo()
    acoes_disponiveis = []

    for arma in personagem.armas:
        acoes_disponiveis.append({"tipo": "arma",  "id": arma.id})

    for magia in personagem.magias:
        if magia.custo_mana <= personagem.mana:
            acoes_disponiveis.append({"tipo": "magia", "id": magia.id})

    return acoes_disponiveis

def aplica_acao(estado: EstadoDuelo, acao: dict):
    novo = deepcopy(estado)
    ativo = novo.personagem_ativo()
    alvo = novo.personagem_passivo()

    if acao["tipo"] == "arma":
        for arma in ativo.armas:
            if arma.id == acao["id"]:
                arma_escolhida = arma
                break

        alvo.vida -= arma_escolhida.dano
        alvo.vida = max(0, alvo.vida)
        novo.log.append(f"{ativo.nome} usou {arma_escolhida.nome} e causou {arma_escolhida.dano} de dano")

    if acao["tipo"] == "magia":
        for magia in ativo.magias:
            if magia.id == acao["id"]:
                magia_escolhida = magia
                break

        ativo.mana -= magia_escolhida.custo_mana 
        ativo.mana = max(0, ativo.mana)

        if magia_escolhida.dano < 0:
            ativo.vida -= magia_escolhida.dano
            novo.log.append(f"{ativo.nome} usou {magia_escolhida.nome} e recuperou {-magia_escolhida.dano} de vida")
        else:
            alvo.vida -= magia_escolhida.dano
            alvo.vida = max(0, alvo.vida)
            novo.log.append(f"{ativo.nome} usou {magia_escolhida.nome} e causou {magia_escolhida.dano} de dano")

    novo.trocar_turno()
    return novo

def negamax(estado: EstadoDuelo, profundidade, alfa, beta) -> int:
    if estado.encerrado() or profundidade == 0:
        return heuristica(estado)
    
    melhor_valor = -math.inf
    for acao in gera_acoes(estado):
        novo_estado = aplica_acao(estado, acao)

        valor = -negamax(novo_estado, profundidade - 1, -beta, -alfa)

        if valor > melhor_valor:
            melhor_valor = valor

        if valor > alfa:
            alfa = valor

        if valor >= beta:
            break

    return melhor_valor

def escolher_melhor_acao(estado : EstadoDuelo, profundidade=4) -> dict:
    melhor_acao = None
    melhor_valor = -math.inf

    for acao in gera_acoes(estado):
        novo_estado = aplica_acao(estado, acao)
        valor = -negamax(novo_estado, profundidade - 1, -math.inf, math.inf)

        if valor > melhor_valor:
            melhor_valor = valor
            melhor_acao = acao

    return melhor_acao