from collections import deque
from dataclasses import dataclass
from typing import Callable, Generic, Iterable, Iterator, TypeVar


T = TypeVar("T")


class Queue(Generic[T]):
    """Fila FIFO com entrada e saida O(1)."""

    def __init__(self, itens: Iterable[T] | None = None) -> None:
        self._dados: deque[T] = deque(itens or [])

    def enqueue(self, item: T) -> None:
        self._dados.append(item)

    def dequeue(self) -> T | None:
        if not self._dados:
            return None
        return self._dados.popleft()

    def peek(self) -> T | None:
        if not self._dados:
            return None
        return self._dados[0]

    def remove_if(self, predicate: Callable[[T], bool]) -> T | None:
        kept: deque[T] = deque()
        found: T | None = None
        while self._dados:
            item = self._dados.popleft()
            if found is None and predicate(item):
                found = item
            else:
                kept.append(item)
        self._dados = kept
        return found

    def __len__(self) -> int:
        return len(self._dados)

    def __iter__(self) -> Iterator[T]:
        return iter(self._dados)


class Stack(Generic[T]):
    """Pilha LIFO para desfazer a ultima finalizacao."""

    def __init__(self, itens: Iterable[T] | None = None) -> None:
        self._dados = list(itens or [])

    def push(self, item: T) -> None:
        self._dados.append(item)

    def pop(self) -> T | None:
        if not self._dados:
            return None
        return self._dados.pop()

    def __len__(self) -> int:
        return len(self._dados)

    def __iter__(self) -> Iterator[T]:
        return iter(self._dados)


@dataclass
class Node(Generic[T]):
    valor: T
    proximo: "Node[T] | None" = None


class LinkedList(Generic[T]):
    """Lista encadeada usada para manter clientes ativos."""

    def __init__(self, itens: Iterable[T] | None = None) -> None:
        self.head: Node[T] | None = None
        self.tail: Node[T] | None = None
        for item in itens or []:
            self.append(item)

    def append(self, item: T) -> None:
        node = Node(item)
        if self.tail is None:
            self.head = node
            self.tail = node
            return
        self.tail.proximo = node
        self.tail = node

    def remove_if(self, predicate: Callable[[T], bool]) -> list[T]:
        removidos: list[T] = []
        anterior: Node[T] | None = None
        atual = self.head
        while atual:
            if predicate(atual.valor):
                removidos.append(atual.valor)
                if anterior:
                    anterior.proximo = atual.proximo
                else:
                    self.head = atual.proximo
                if atual is self.tail:
                    self.tail = anterior
                atual = atual.proximo
            else:
                anterior = atual
                atual = atual.proximo
        return removidos

    def to_list(self) -> list[T]:
        return list(self)

    def __iter__(self) -> Iterator[T]:
        atual = self.head
        while atual:
            yield atual.valor
            atual = atual.proximo


def binary_search_recursive(
    vetor: list[T],
    alvo: int,
    key: Callable[[T], int],
    inicio: int = 0,
    fim: int | None = None,
) -> T | None:
    """Busca binaria recursiva em vetor ordenado por id: O(log n)."""
    if fim is None:
        fim = len(vetor) - 1
    if inicio > fim:
        return None
    meio = (inicio + fim) // 2
    valor = key(vetor[meio])
    if valor == alvo:
        return vetor[meio]
    if alvo < valor:
        return binary_search_recursive(vetor, alvo, key, inicio, meio - 1)
    return binary_search_recursive(vetor, alvo, key, meio + 1, fim)


def merge_sort(items: list[T], key: Callable[[T], object]) -> list[T]:
    """Ordenacao estavel para relatorios: O(n log n)."""
    if len(items) <= 1:
        return items[:]
    meio = len(items) // 2
    esquerda = merge_sort(items[:meio], key)
    direita = merge_sort(items[meio:], key)
    return _merge(esquerda, direita, key)


def _merge(esquerda: list[T], direita: list[T], key: Callable[[T], object]) -> list[T]:
    resultado: list[T] = []
    i = 0
    j = 0
    while i < len(esquerda) and j < len(direita):
        if key(esquerda[i]) <= key(direita[j]):
            resultado.append(esquerda[i])
            i += 1
        else:
            resultado.append(direita[j])
            j += 1
    resultado.extend(esquerda[i:])
    resultado.extend(direita[j:])
    return resultado

