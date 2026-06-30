from ontologia import Personagem, Arma, Magia

# Criando mais de 8 instancias como pedidas (4 Armas + 3 Magias + 4 Personagens = 11 instancias)

# --- Armas ---
espada_longa = Arma(nome="Espada Longa", dano=15)
adaga = Arma(nome="Adaga Envenenada", dano=8)
cajado = Arma(nome="Cajado Mistico", dano=5)
arco = Arma(nome="Arco Longo", dano=12)

# --- Magias ---
bola_fogo = Magia(nome="Bola de Fogo", dano=25, custo_mana=10)
cura = Magia(nome="Cura Divina", dano=-20, custo_mana=15)
raio_gelo = Magia(nome="Raio de Gelo", dano=18, custo_mana=12)

# --- Personagens ---
arthur = Personagem(nome="Heroi Arthur", vida=100, mana=20, arma=espada_longa)
mago_negro = Personagem(nome="Vilao Mago Negro", vida=80, mana=50, arma=cajado, magias=[bola_fogo, cura])
grom = Personagem(nome="Guerreiro Grom", vida=120, mana=10, arma=adaga)
legolas = Personagem(nome="Arqueiro Legolas", vida=90, mana=30, arma=arco, magias=[raio_gelo])
