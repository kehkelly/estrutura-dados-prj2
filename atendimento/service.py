import logging
from datetime import datetime
from pathlib import Path

from atendimento.models import (
    Atendente,
    Atendimento,
    Cliente,
    Ticket,
    agora_iso,
    to_dict,
)
from atendimento.storage import (
    JsonStorage,
    atendimento_from_dict,
    atendente_from_dict,
    cliente_from_dict,
    ticket_from_dict,
)
from atendimento.structures import (
    LinkedList,
    Queue,
    Stack,
    binary_search_recursive,
)


LOG_PATH = Path("data/operations.log")
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class AtendimentoService:
    def __init__(self, storage: JsonStorage | None = None) -> None:
        self.storage = storage or JsonStorage()
        self.clientes: list[Cliente] = []
        self.atendentes: list[Atendente] = []
        self.fila_comum: Queue[Ticket] = Queue()
        self.fila_prioridade: Queue[Ticket] = Queue()
        self.historico: list[Atendimento] = []
        self.desfazer: Stack[Atendimento] = Stack()
        self.clientes_ativos = LinkedList[Cliente]()
        self.load()

    def load(self) -> None:
        state = self.storage.load()
        self.clientes = [cliente_from_dict(item) for item in state["clientes"]]
        self.atendentes = [atendente_from_dict(item) for item in state["atendentes"]]
        self.fila_comum = Queue(ticket_from_dict(item) for item in state["fila_comum"])
        self.fila_prioridade = Queue(
            ticket_from_dict(item) for item in state["fila_prioridade"]
        )
        self.historico = [
            atendimento_from_dict(item) for item in state["historico"]
        ]
        self.desfazer = Stack(
            atendimento_from_dict(item) for item in state["desfazer"]
        )
        self._rebuild_clientes_ativos()

    def save(self) -> None:
        self.storage.save(
            {
                "clientes": [to_dict(item) for item in self.clientes],
                "atendentes": [to_dict(item) for item in self.atendentes],
                "fila_comum": [to_dict(item) for item in self.fila_comum],
                "fila_prioridade": [to_dict(item) for item in self.fila_prioridade],
                "historico": [to_dict(item) for item in self.historico],
                "desfazer": [to_dict(item) for item in self.desfazer],
            }
        )

    def cadastrar_cliente(
        self,
        cliente_id: int,
        nome: str,
        telefone: str,
        prioridade: bool,
    ) -> Cliente:
        if cliente_id <= 0:
            raise ValueError("Id do cliente deve ser positivo.")
        if not nome.strip():
            raise ValueError("Nome do cliente e obrigatorio.")
        if self.buscar_cliente(cliente_id):
            raise ValueError("Ja existe cliente com esse id.")
        cliente = Cliente(cliente_id, nome.strip(), telefone.strip(), prioridade)
        self.clientes.append(cliente)
        self.clientes.sort(key=lambda item: item.id)
        self.clientes_ativos.append(cliente)
        self.save()
        logging.info("Cliente cadastrado: %s", cliente_id)
        return cliente

    def cadastrar_atendente(self, atendente_id: int, nome: str) -> Atendente:
        if atendente_id <= 0:
            raise ValueError("Id do atendente deve ser positivo.")
        if not nome.strip():
            raise ValueError("Nome do atendente e obrigatorio.")
        if self.buscar_atendente(atendente_id):
            raise ValueError("Ja existe atendente com esse id.")
        atendente = Atendente(atendente_id, nome.strip())
        self.atendentes.append(atendente)
        self.save()
        logging.info("Atendente cadastrado: %s", atendente_id)
        return atendente

    def abrir_atendimento(self, cliente_id: int) -> Ticket:
        cliente = self.buscar_cliente(cliente_id)
        if cliente is None or not cliente.ativo:
            raise ValueError("Cliente nao encontrado ou inativo.")
        if self.cliente_em_aberto(cliente_id):
            raise ValueError("Cliente possui atendimento em aberto.")
        ticket = Ticket(cliente_id, agora_iso(), cliente.prioridade)
        if cliente.prioridade:
            self.fila_prioridade.enqueue(ticket)
        else:
            self.fila_comum.enqueue(ticket)
        self.save()
        logging.info("Atendimento aberto para cliente: %s", cliente_id)
        return ticket

    def chamar_proximo(self, atendente_id: int) -> Ticket:
        atendente = self.buscar_atendente(atendente_id)
        if atendente is None:
            raise ValueError("Atendente nao encontrado.")
        if atendente.cliente_atual_id is not None:
            raise ValueError("Atendente ja esta em atendimento.")
        ticket = self.fila_prioridade.dequeue() or self.fila_comum.dequeue()
        if ticket is None:
            raise ValueError("Nao ha clientes na fila.")
        atendente.cliente_atual_id = ticket.cliente_id
        atendente.inicio_atendimento = agora_iso()
        self.save()
        logging.info(
            "Cliente %s chamado por atendente %s",
            ticket.cliente_id,
            atendente_id,
        )
        return ticket

    def finalizar_atendimento(
        self,
        atendente_id: int,
        duracao_minutos: int | None = None,
    ) -> Atendimento:
        atendente = self.buscar_atendente(atendente_id)
        if atendente is None:
            raise ValueError("Atendente nao encontrado.")
        if atendente.cliente_atual_id is None:
            raise ValueError("Atendente nao possui atendimento em aberto.")
        if duracao_minutos is None:
            duracao_minutos = self._calcular_duracao(atendente.inicio_atendimento)
        if duracao_minutos <= 0:
            raise ValueError("Duracao deve ser positiva.")
        atendimento = Atendimento(
            cliente_id=atendente.cliente_atual_id,
            atendente_id=atendente.id,
            data=agora_iso()[:10],
            duracao_minutos=duracao_minutos,
            finalizado_em=agora_iso(),
        )
        self.historico.append(atendimento)
        self.desfazer.push(atendimento)
        atendente.cliente_atual_id = None
        atendente.inicio_atendimento = None
        self.save()
        logging.info("Atendimento finalizado: %s", to_dict(atendimento))
        return atendimento

    def desfazer_ultima_finalizacao(self) -> Atendimento:
        atendimento = self.desfazer.pop()
        if atendimento is None:
            raise ValueError("Nao ha finalizacao para desfazer.")
        for indice in range(len(self.historico) - 1, -1, -1):
            atual = self.historico[indice]
            if atual == atendimento:
                self.historico.pop(indice)
                break
        else:
            raise ValueError("Finalizacao nao encontrada no historico.")
        atendente = self.buscar_atendente(atendimento.atendente_id)
        if atendente and atendente.cliente_atual_id is None:
            atendente.cliente_atual_id = atendimento.cliente_id
            atendente.inicio_atendimento = agora_iso()
        self.save()
        logging.info("Finalizacao desfeita: %s", to_dict(atendimento))
        return atendimento

    def remover_clientes_inativos(self) -> list[Cliente]:
        removidos = self.clientes_ativos.remove_if(
            lambda cliente: not self.cliente_em_aberto(cliente.id)
            and len(self.historico_por_cliente(cliente.id)) == 0
        )
        ids = {cliente.id for cliente in removidos}
        for cliente in self.clientes:
            if cliente.id in ids:
                cliente.ativo = False
        self.save()
        logging.info("Clientes inativados: %s", sorted(ids))
        return removidos

    def buscar_cliente(self, cliente_id: int) -> Cliente | None:
        vetor_ordenado = sorted(self.clientes, key=lambda item: item.id)
        return binary_search_recursive(vetor_ordenado, cliente_id, lambda item: item.id)

    def buscar_atendente(self, atendente_id: int) -> Atendente | None:
        for atendente in self.atendentes:
            if atendente.id == atendente_id:
                return atendente
        return None

    def historico_por_cliente(self, cliente_id: int) -> list[Atendimento]:
        return [item for item in self.historico if item.cliente_id == cliente_id]

    def cliente_em_aberto(self, cliente_id: int) -> bool:
        if any(ticket.cliente_id == cliente_id for ticket in self.fila_comum):
            return True
        if any(ticket.cliente_id == cliente_id for ticket in self.fila_prioridade):
            return True
        return any(
            atendente.cliente_atual_id == cliente_id for atendente in self.atendentes
        )

    def listar_filas(self) -> dict[str, list[Ticket]]:
        return {
            "prioridade": list(self.fila_prioridade),
            "comum": list(self.fila_comum),
        }

    def alertas_espera_alta(self, limite_minutos: int = 30) -> list[Ticket]:
        agora = datetime.now()
        tickets = list(self.fila_prioridade) + list(self.fila_comum)
        alertas = []
        for ticket in tickets:
            aberto = datetime.fromisoformat(ticket.aberto_em)
            espera = int((agora - aberto).total_seconds() // 60)
            if espera >= limite_minutos:
                alertas.append(ticket)
        return alertas

    def _rebuild_clientes_ativos(self) -> None:
        self.clientes_ativos = LinkedList(
            cliente for cliente in self.clientes if cliente.ativo
        )

    @staticmethod
    def _calcular_duracao(inicio: str | None) -> int:
        if inicio is None:
            return 1
        segundos = (datetime.now() - datetime.fromisoformat(inicio)).total_seconds()
        return max(1, int(segundos // 60))

