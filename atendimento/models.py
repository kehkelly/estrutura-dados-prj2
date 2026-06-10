from dataclasses import asdict, dataclass
from datetime import datetime 
from typing import Any


@dataclass
class Cliente:
    id: int
    nome: str
    telefone: str
    prioridade: bool
    ativo: bool = True


@dataclass
class Atendente:
    id: int
    nome: str
    cliente_atual_id: int | None = None
    inicio_atendimento: str | None = None


@dataclass
class Ticket:
    cliente_id: int
    aberto_em: str
    prioridade: bool


@dataclass
class Atendimento:
    cliente_id: int
    atendente_id: int
    data: str
    duracao_minutos: int
    finalizado_em: str


def agora_iso() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


def to_dict(obj: Any) -> dict[str, Any]:
    return asdict(obj)

