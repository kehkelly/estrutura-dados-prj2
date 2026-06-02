# Relatorio tecnico curto

## Objetivo

O projeto implementa um sistema de gerenciamento de atendimentos para uma
clinica ou central de atendimento. Ele permite cadastrar clientes e atendentes,
abrir filas, chamar e finalizar atendimentos, consultar historico, desfazer a
ultima finalizacao e gerar relatorios.

## Estruturas usadas

- Vetor ordenado: `self.clientes` e mantido ordenado por `id` para permitir
  busca binaria.
- Vetor nao ordenado: `self.atendentes` guarda cadastros temporarios/listagem
  simples de atendentes.
- Fila comum: `Queue`, baseada em `deque`, controla clientes normais em ordem
  de chegada.
- Fila de prioridade: outra `Queue`, tambem FIFO, chamada antes da fila comum.
- Pilha: `Stack` armazena finalizacoes para desfazer a ultima acao.
- Lista encadeada: `LinkedList` representa a lista de clientes ativos e e usada
  na rotina de remocao/inativacao.
- Ordenacao: `merge_sort` ordena dados de relatorio.
- Recursao: `binary_search_recursive` faz a busca binaria recursiva por id.

## Big-O

- Cadastro de cliente: O(n log n), pois o vetor e reordenado por id.
- Busca rapida de cliente: O(log n), usando busca binaria no vetor ordenado.
- Entrada na fila: O(1), com `deque.append`.
- Chamada do proximo atendimento: O(1), pois remove do inicio com
  `deque.popleft`.
- Finalizacao: O(1) para registrar historico e empilhar acao de desfazer.
- Desfazer finalizacao: O(n), pois remove a ultima ocorrencia do historico.
- Remover clientes inativos: O(n), percorrendo a lista encadeada.
- Relatorios ordenados: O(n log n), usando merge sort.

## Decisoes de negocio

Clientes com prioridade sao sempre chamados antes dos clientes comuns. Dentro da
fila de prioridade a ordem de chegada e preservada. Um atendente nao pode chamar
outro cliente enquanto esta ocupado. O sistema bloqueia finalizacao sem
atendimento aberto e impede inativar cliente com atendimento em fila ou em
execucao.

## Persistencia e logs

Os dados ficam em `data/state.json`. As operacoes importantes sao registradas em
`data/operations.log`. O arquivo `data/sample_state.json` contem dados de
exemplo para demonstracao.

