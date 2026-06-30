from dataclasses import dataclass
from ontologia import Personagem

# Guarda o snapshot (estado atual) do jogo
@dataclass
class EstadoDuelo:
    personagem_1: Personagem
    personagem_2: Personagem
    turno_do_p1: bool = True  # Define de quem e o turno