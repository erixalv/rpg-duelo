from dataclasses import dataclass, field
from typing import List, Optional

# Definindo a base de dados com dataclasses Python
@dataclass
class Arma:
    nome: str
    dano: int

@dataclass
class Magia:
    nome: str
    dano: int
    custo_mana: int

@dataclass
class Personagem:
    nome: str
    vida: int
    mana: int
    arma: Optional[Arma] = None
    magias: List[Magia] = field(default_factory=list)
