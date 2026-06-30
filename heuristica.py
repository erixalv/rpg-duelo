from estado_duelo import EstadoDuelo

def avaliar_estado(estado: EstadoDuelo) -> int:
    # Comentario: Calcula o score baseado na heuristica de vida + dano potencial
    p1 = estado.personagem_1
    p2 = estado.personagem_2

    # Dano potencial P1
    dano_p1 = p1.arma.dano if p1.arma else 0
    if p1.magias:
        dano_p1 += sum(m.dano for m in p1.magias if m.dano > 0)
        
    # Dano potencial P2
    dano_p2 = p2.arma.dano if p2.arma else 0
    if p2.magias:
        dano_p2 += sum(m.dano for m in p2.magias if m.dano > 0)

    # Score final e a diferenca entre o Player 1 e o Player 2
    return (p1.vida + dano_p1) - (p2.vida + dano_p2)