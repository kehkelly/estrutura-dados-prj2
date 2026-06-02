import csv
from collections import Counter
from pathlib import Path

from atendimento.models import Atendimento
from atendimento.service import AtendimentoService
from atendimento.structures import merge_sort


def filtrar_por_data(
    historico: list[Atendimento],
    data_inicio: str | None = None,
    data_fim: str | None = None,
) -> list[Atendimento]:
    resultado = []
    for item in historico:
        if data_inicio and item.data < data_inicio:
            continue
        if data_fim and item.data > data_fim:
            continue
        resultado.append(item)
    return resultado


def tempo_medio(service: AtendimentoService) -> float:
    if not service.historico:
        return 0.0
    total = sum(item.duracao_minutos for item in service.historico)
    return total / len(service.historico)


def top_clientes_mais_atendidos(
    service: AtendimentoService,
    limite: int = 5,
) -> list[tuple[int, str, int]]:
    contador = Counter(item.cliente_id for item in service.historico)
    linhas = []
    for cliente_id, total in contador.items():
        cliente = service.buscar_cliente(cliente_id)
        nome = cliente.nome if cliente else "Cliente removido"
        linhas.append((cliente_id, nome, total))
    ordenadas = merge_sort(linhas, key=lambda item: (-item[2], item[1]))
    return ordenadas[:limite]


def historico_ordenado_por_duracao(
    service: AtendimentoService,
) -> list[Atendimento]:
    return merge_sort(service.historico, key=lambda item: item.duracao_minutos)


def exportar_csv(
    service: AtendimentoService,
    caminho: str | Path = "data/relatorio.csv",
    data_inicio: str | None = None,
    data_fim: str | None = None,
) -> Path:
    destino = Path(caminho)
    destino.parent.mkdir(parents=True, exist_ok=True)
    historico = filtrar_por_data(service.historico, data_inicio, data_fim)
    with destino.open("w", newline="", encoding="utf-8") as arquivo:
        writer = csv.writer(arquivo)
        writer.writerow(
            [
                "cliente_id",
                "cliente_nome",
                "atendente_id",
                "data",
                "duracao_minutos",
                "finalizado_em",
            ]
        )
        for item in historico:
            cliente = service.buscar_cliente(item.cliente_id)
            writer.writerow(
                [
                    item.cliente_id,
                    cliente.nome if cliente else "",
                    item.atendente_id,
                    item.data,
                    item.duracao_minutos,
                    item.finalizado_em,
                ]
            )
    return destino

