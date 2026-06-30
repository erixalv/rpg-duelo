from ontologia import Personagem, Arma, Magia

# --- Armas ---
espada_longa = Arma(nome="Espada Longa", dano=16)
machado = Arma(nome="Machado Pesado", dano=20)
cajado = Arma(nome="Cajado Quebrado", dano=6)
arco = Arma(nome="Arco Longo", dano=12)

# --- Magias ---
bola_fogo = Magia(nome="Bola de Fogo", dano=26, custo_mana=15)
cura_divina = Magia(nome="Cura Divina", dano=-30, custo_mana=20)
cura_menor = Magia(nome="Poção Menor", dano=-15, custo_mana=10)
flecha_magica = Magia(nome="Flecha de Gelo", dano=22, custo_mana=10)
golpe_fatal = Magia(nome="Golpe Esmagador", dano=35, custo_mana=15)

# --- Personagens ---
# Arthur: Equilibrado. Bom dano físico, possui uma cura de emergência.
arthur = Personagem(nome="Herói Arthur", vida=110, mana=20, arma=espada_longa, magias=[cura_divina])

# Mago Negro: Pouquíssima vida, muito fraco sem mana, mas um poder mágico devastador.
mago_negro = Personagem(nome="Vilão Mago Negro", vida=75, mana=45, arma=cajado, magias=[bola_fogo, cura_menor])

# Grom: Bárbaro com muita vida e um único golpe explosivo (gasta toda sua mana de uma vez).
grom = Personagem(nome="Guerreiro Grom", vida=130, mana=15, arma=machado, magias=[golpe_fatal])

# Legolas: Atirador tático. Combina ataques rápidos do arco com flechas mágicas de baixo custo.
legolas = Personagem(nome="Arqueiro Legolas", vida=90, mana=30, arma=arco, magias=[flecha_magica])