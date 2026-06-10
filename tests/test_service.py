import tempfile
import unittest
from pathlib import Path

from atendimento.reports import exportar_csv, tempo_medio, top_clientes_mais_atendidos
from atendimento.service import AtendimentoService
from atendimento.storage import JsonStorage 


class AtendimentoServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.storage = JsonStorage(Path(self.tmp.name) / "state.json")
        self.service = AtendimentoService(self.storage)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_busca_binaria_cliente(self) -> None:
        self.service.cadastrar_cliente(20, "Bia", "2222", False)
        self.service.cadastrar_cliente(10, "Ana", "1111", True)

        cliente = self.service.buscar_cliente(10)

        self.assertIsNotNone(cliente)
        self.assertEqual(cliente.nome, "Ana")

    def test_prioridade_chamada_antes_da_fila_comum(self) -> None:
        self.service.cadastrar_cliente(1, "Comum", "1111", False)
        self.service.cadastrar_cliente(2, "Urgente", "2222", True)
        self.service.cadastrar_atendente(1, "Ruben")
        self.service.abrir_atendimento(1)
        self.service.abrir_atendimento(2)

        ticket = self.service.chamar_proximo(1)

        self.assertEqual(ticket.cliente_id, 2)

    def test_finalizar_e_desfazer(self) -> None:
        self.service.cadastrar_cliente(1, "Ana", "1111", False)
        self.service.cadastrar_atendente(1, "Ruben")
        self.service.abrir_atendimento(1)
        self.service.chamar_proximo(1)
        atendimento = self.service.finalizar_atendimento(1, 12)

        self.assertEqual(len(self.service.historico), 1)
        desfeito = self.service.desfazer_ultima_finalizacao()

        self.assertEqual(desfeito, atendimento)
        self.assertEqual(len(self.service.historico), 0)
        self.assertEqual(self.service.buscar_atendente(1).cliente_atual_id, 1)

    def test_nao_remove_cliente_em_atendimento_aberto(self) -> None:
        self.service.cadastrar_cliente(1, "Ana", "1111", False)
        self.service.cadastrar_cliente(2, "Bia", "2222", False)
        self.service.abrir_atendimento(1)

        removidos = self.service.remover_clientes_inativos()

        self.assertEqual([cliente.id for cliente in removidos], [2])
        self.assertTrue(self.service.buscar_cliente(1).ativo)
        self.assertFalse(self.service.buscar_cliente(2).ativo)

    def test_relatorios_e_csv(self) -> None:
        self.service.cadastrar_cliente(1, "Ana", "1111", False)
        self.service.cadastrar_atendente(1, "Ruben")
        for duracao in (10, 20):
            self.service.abrir_atendimento(1)
            self.service.chamar_proximo(1)
            self.service.finalizar_atendimento(1, duracao)

        caminho = exportar_csv(self.service, Path(self.tmp.name) / "relatorio.csv")

        self.assertEqual(tempo_medio(self.service), 15)
        self.assertEqual(top_clientes_mais_atendidos(self.service)[0][2], 2)
        self.assertTrue(caminho.exists())


if __name__ == "__main__":
    unittest.main()

