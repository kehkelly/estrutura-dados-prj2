import json
from pathlib import Path
from typing import Any 

from atendimento.models import Atendente, Atendimento, Cliente, Ticket


DEFAULT_STATE = {
    "clientes": [],
    "atendentes": [],
    "fila_comum": [],
    "fila_prioridade": [],
    "historico": [],
    "desfazer": [],
}


class JsonStorage:
    def __init__(self, caminho: str | Path = "data/state.json") -> None:
        self.caminho = Path(caminho)

    def load(self) -> dict[str, Any]:
        if not self.caminho.exists():
            return json.loads(json.dumps(DEFAULT_STATE))
        with self.caminho.open("r", encoding="utf-8") as arquivo:
            return json.load(arquivo)

    def save(self, state: dict[str, Any]) -> None:
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        with self.caminho.open("w", encoding="utf-8") as arquivo:
            json.dump(state, arquivo, ensure_ascii=False, indent=2)


def cliente_from_dict(data: dict[str, Any]) -> Cliente:
    return Cliente(**data)


def atendente_from_dict(data: dict[str, Any]) -> Atendente:
    return Atendente(**data)


def ticket_from_dict(data: dict[str, Any]) -> Ticket:
    return Ticket(**data)


def atendimento_from_dict(data: dict[str, Any]) -> Atendimento:
    return Atendimento(**data)

