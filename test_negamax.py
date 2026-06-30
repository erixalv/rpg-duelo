import unittest
import math
from ontologia import Personagem, Arma, Magia
from estado_duelo import EstadoDuelo
from negamax import (
    gera_acoes,
    aplica_acao,
    negamax,
    escolher_melhor_acao,
    duelo_encerrado,
    vencedor,
    personagem_ativo,
    personagem_passivo,
)
from heuristica import avaliar_estado


def personagem_base(nome="Herói", vida=100, mana=50):
    """Fábrica auxiliar — cria um personagem sem arma nem magias."""
    return Personagem(nome=nome, vida=vida, mana=mana, arma=None, magias=[])


def estado_simples(vida_p1=100, vida_p2=100, mana_p1=50, mana_p2=50, turno_do_p1=True):
    """Fábrica auxiliar — monta um EstadoDuelo do zero para os testes."""
    p1 = personagem_base(nome="Jogador", vida=vida_p1, mana=mana_p1)
    p2 = personagem_base(nome="IA", vida=vida_p2, mana=mana_p2)
    return EstadoDuelo(personagem_1=p1, personagem_2=p2, turno_do_p1=turno_do_p1)


# ─────────────────────────────────────────
#  Testes das funções auxiliares
# ─────────────────────────────────────────

class TesteAuxiliares(unittest.TestCase):

    def test_personagem_ativo_quando_turno_p1(self):
        estado = estado_simples(turno_do_p1=True)
        self.assertIs(personagem_ativo(estado), estado.personagem_1)

    def test_personagem_ativo_quando_turno_p2(self):
        estado = estado_simples(turno_do_p1=False)
        self.assertIs(personagem_ativo(estado), estado.personagem_2)

    def test_personagem_passivo_e_o_oposto_do_ativo(self):
        estado = estado_simples(turno_do_p1=True)
        self.assertIs(personagem_passivo(estado), estado.personagem_2)

    def test_duelo_nao_encerrado_com_ambos_vivos(self):
        estado = estado_simples(vida_p1=50, vida_p2=50)
        self.assertFalse(duelo_encerrado(estado))

    def test_duelo_encerrado_quando_p2_morre(self):
        estado = estado_simples(vida_p2=0)
        self.assertTrue(duelo_encerrado(estado))
        self.assertEqual(vencedor(estado), "p1")

    def test_duelo_encerrado_quando_p1_morre(self):
        estado = estado_simples(vida_p1=0)
        self.assertTrue(duelo_encerrado(estado))
        self.assertEqual(vencedor(estado), "p2")

    def test_sem_vencedor_quando_ambos_vivos(self):
        estado = estado_simples()
        self.assertIsNone(vencedor(estado))


# ─────────────────────────────────────────
#  Testes de gera_acoes
# ─────────────────────────────────────────

class TesteGeraAcoes(unittest.TestCase):

    def test_sem_arma_sem_magia_retorna_lista_vazia(self):
        estado = estado_simples()
        self.assertEqual(gera_acoes(estado), [])

    def test_atacar_incluido_quando_tem_arma(self):
        estado = estado_simples()
        estado.personagem_1.arma = Arma(nome="Espada", dano=25)

        acoes = gera_acoes(estado)

        self.assertIn({"tipo": "atacar"}, acoes)

    def test_magia_incluida_quando_tem_mana(self):
        estado = estado_simples(mana_p1=30)
        estado.personagem_1.magias = [Magia(nome="Fogo", dano=40, custo_mana=20)]

        acoes = gera_acoes(estado)

        self.assertIn({"tipo": "magia", "nome_magia": "Fogo"}, acoes)

    def test_magia_excluida_quando_sem_mana(self):
        estado = estado_simples(mana_p1=10)
        estado.personagem_1.magias = [Magia(nome="Fogo", dano=40, custo_mana=20)]

        acoes = gera_acoes(estado)

        self.assertNotIn({"tipo": "magia", "nome_magia": "Fogo"}, acoes)

    def test_considera_o_personagem_ativo_correto(self):
        # turno é do p2 — ações devem vir do p2, não do p1
        estado = estado_simples(turno_do_p1=False)
        estado.personagem_1.arma = Arma(nome="Espada", dano=25)
        estado.personagem_2.arma = Arma(nome="Machado", dano=30)

        acoes = gera_acoes(estado)

        # Só existe uma ação possível: atacar (a arma do p2)
        self.assertEqual(acoes, [{"tipo": "atacar"}])


# ─────────────────────────────────────────
#  Testes de aplica_acao
# ─────────────────────────────────────────

class TesteAplicaAcao(unittest.TestCase):

    def test_atacar_reduz_vida_do_alvo(self):
        estado = estado_simples(vida_p2=100)
        estado.personagem_1.arma = Arma(nome="Espada", dano=25)

        novo = aplica_acao(estado, {"tipo": "atacar"})

        self.assertEqual(novo.personagem_2.vida, 75)

    def test_vida_nao_fica_negativa(self):
        estado = estado_simples(vida_p2=10)
        estado.personagem_1.arma = Arma(nome="Espada", dano=9999)

        novo = aplica_acao(estado, {"tipo": "atacar"})

        self.assertEqual(novo.personagem_2.vida, 0)

    def test_magia_reduz_vida_do_alvo(self):
        estado = estado_simples(vida_p2=100, mana_p1=50)
        estado.personagem_1.magias = [Magia(nome="Fogo", dano=40, custo_mana=20)]

        novo = aplica_acao(estado, {"tipo": "magia", "nome_magia": "Fogo"})

        self.assertEqual(novo.personagem_2.vida, 60)

    def test_magia_desconta_mana_do_ativo_nao_do_alvo(self):
        estado = estado_simples(mana_p1=50, mana_p2=50)
        estado.personagem_1.magias = [Magia(nome="Fogo", dano=40, custo_mana=20)]

        novo = aplica_acao(estado, {"tipo": "magia", "nome_magia": "Fogo"})

        self.assertEqual(novo.personagem_1.mana, 30)  # quem usou perdeu mana
        self.assertEqual(novo.personagem_2.mana, 50)  # alvo não perde mana

    def test_magia_de_cura_tem_dano_negativo(self):
        # Cura Divina tem dano=-20 — deve aumentar a vida do alvo (que é quem usa, na prática
        # a Pessoa A modelou cura como "dano negativo no alvo" — aqui validamos o comportamento real)
        estado = estado_simples(vida_p2=80, mana_p1=50)
        estado.personagem_1.magias = [Magia(nome="Cura Divina", dano=-20, custo_mana=15)]

        novo = aplica_acao(estado, {"tipo": "magia", "nome_magia": "Cura Divina"})

        # vida -= -20  →  vida aumenta em 20
        self.assertEqual(novo.personagem_2.vida, 100)

    def test_turno_troca_apos_acao(self):
        estado = estado_simples(turno_do_p1=True)
        estado.personagem_1.arma = Arma(nome="Espada", dano=10)

        novo = aplica_acao(estado, {"tipo": "atacar"})

        self.assertFalse(novo.turno_do_p1)

    def test_estado_original_nao_e_modificado(self):
        estado = estado_simples(vida_p2=100)
        estado.personagem_1.arma = Arma(nome="Espada", dano=25)

        aplica_acao(estado, {"tipo": "atacar"})

        self.assertEqual(estado.personagem_2.vida, 100)
        self.assertTrue(estado.turno_do_p1)

    def test_magia_inexistente_levanta_erro(self):
        estado = estado_simples(mana_p1=50)
        estado.personagem_1.magias = [Magia(nome="Fogo", dano=40, custo_mana=20)]

        with self.assertRaises(ValueError):
            aplica_acao(estado, {"tipo": "magia", "nome_magia": "Não Existe"})


# ─────────────────────────────────────────
#  Testes de negamax
# ─────────────────────────────────────────

class TesteNegamax(unittest.TestCase):

    def test_profundidade_zero_retorna_heuristica_do_turno_p1(self):
        estado = estado_simples(vida_p1=70, vida_p2=50, turno_do_p1=True)

        resultado = negamax(estado, profundidade=0, alfa=-9999, beta=9999)

        self.assertEqual(resultado, avaliar_estado(estado))

    def test_profundidade_zero_inverte_sinal_no_turno_p2(self):
        estado = estado_simples(vida_p1=70, vida_p2=50, turno_do_p1=False)

        resultado = negamax(estado, profundidade=0, alfa=-9999, beta=9999)

        self.assertEqual(resultado, -avaliar_estado(estado))

    def test_estado_encerrado_retorna_heuristica(self):
        estado = estado_simples(vida_p2=0, turno_do_p1=True)

        resultado = negamax(estado, profundidade=3, alfa=-9999, beta=9999)

        self.assertEqual(resultado, avaliar_estado(estado))

    def test_retorna_numero(self):
        estado = estado_simples()
        estado.personagem_1.arma = Arma(nome="Espada", dano=10)

        resultado = negamax(estado, profundidade=1, alfa=-9999, beta=9999)

        self.assertIsInstance(resultado, (int, float))


# ─────────────────────────────────────────
#  Testes de escolher_melhor_acao
# ─────────────────────────────────────────

class TesteEscolherMelhorAcao(unittest.TestCase):

    def test_escolhe_atacar_quando_e_a_unica_opcao(self):
        estado = estado_simples(vida_p2=50)
        estado.personagem_1.arma = Arma(nome="Espada", dano=25)

        acao = escolher_melhor_acao(estado, profundidade=2)

        self.assertEqual(acao, {"tipo": "atacar"})

    def test_escolhe_magia_que_mata_quando_ataque_nao_mata(self):
        # IA com 35 de vida: ataque (10) não mata, magia (40) mata
        estado = estado_simples(vida_p2=35, mana_p1=50)
        estado.personagem_1.arma = Arma(nome="Espada", dano=10)
        estado.personagem_1.magias = [Magia(nome="Fogo", dano=40, custo_mana=20)]

        acao = escolher_melhor_acao(estado, profundidade=1)

        self.assertEqual(acao, {"tipo": "magia", "nome_magia": "Fogo"})

    def test_retorna_none_quando_nao_ha_acoes(self):
        estado = estado_simples(mana_p1=0)
        # sem arma, sem mana para a magia
        estado.personagem_1.magias = [Magia(nome="Fogo", dano=40, custo_mana=20)]

        acao = escolher_melhor_acao(estado, profundidade=1)

        self.assertIsNone(acao)


if __name__ == "__main__":
    unittest.main(verbosity=2)