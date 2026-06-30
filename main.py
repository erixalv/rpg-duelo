from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import copy

from estado_duelo import EstadoDuelo
from instancias import arthur, mago_negro

app = FastAPI(title="API RPG Duelo")

# Comentario: Inicia o estado do jogo na memoria usando copias dos personagens base
estado_atual = EstadoDuelo(
    personagem_1=copy.deepcopy(arthur),
    personagem_2=copy.deepcopy(mago_negro),
    turno_do_p1=True
)

class Acao(BaseModel):
    tipo: str # "atacar" ou "magia"
    nome_magia: Optional[str] = None

@app.get("/estado")
def get_estado():
    # Comentario: Retorna o estado completo da partida neste exato momento
    return estado_atual

@app.post("/acao")
def realizar_acao(acao: Acao):
    # Comentario: Recebe uma acao, processa as regras de dano/mana, e retorna o novo estado
    global estado_atual
    
    atacante = estado_atual.personagem_1 if estado_atual.turno_do_p1 else estado_atual.personagem_2
    defensor = estado_atual.personagem_2 if estado_atual.turno_do_p1 else estado_atual.personagem_1

    if acao.tipo == "atacar":
        dano = atacante.arma.dano if atacante.arma else 0
        defensor.vida -= dano
        
    elif acao.tipo == "magia":
        if not acao.nome_magia:
            raise HTTPException(status_code=400, detail="Nome da magia e obrigatorio")
        
        # Busca a magia no arsenal do personagem
        magia_usada = next((m for m in atacante.magias if m.nome == acao.nome_magia), None)
        if not magia_usada:
            raise HTTPException(status_code=400, detail="Magia nao encontrada no personagem")
            
        if atacante.mana < magia_usada.custo_mana:
            raise HTTPException(status_code=400, detail="Mana insuficiente")
            
        # Aplica os custos e os danos da magia
        atacante.mana -= magia_usada.custo_mana
        defensor.vida -= magia_usada.dano
    else:
        raise HTTPException(status_code=400, detail="Acao invalida")

    # Passa a vez para o outro jogador
    estado_atual.turno_do_p1 = not estado_atual.turno_do_p1

    return estado_atual
