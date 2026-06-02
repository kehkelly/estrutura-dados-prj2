# Projeto 2 - Sistema Completo de Atendimento e Analise

Sistema em Python para gerenciamento de atendimentos de uma clinica ou central
de atendimento. O projeto usa filas, pilha, lista encadeada, vetor ordenado,
busca binaria recursiva, ordenacao e persistencia em arquivo.

## Funcionalidades

- Cadastro de clientes com id, nome, telefone e prioridade.
- Cadastro de atendentes.
- Abertura de atendimento com fila comum e fila de prioridade.
- Chamada do proximo cliente, sempre priorizando urgentes e mantendo ordem de
  chegada.
- Finalizacao de atendimento com data, duracao e atendente.
- Historico de atendimentos por cliente.
- Desfazer ultima finalizacao usando pilha.
- Remover/inativar clientes inativos usando lista encadeada.
- Relatorio de tempo medio de atendimento.
- Exportacao de relatorio em CSV.
- Busca rapida de cliente por id com vetor ordenado e busca binaria.
- Extras: filtro por data no CSV, top 5 clientes mais atendidos e alertas de
  espera alta.

## Como executar

O projeto usa apenas biblioteca padrao do Python.

```bash
python -m atendimento
```

No Windows, caso use o launcher:

```bash
py -m atendimento
```

## Como executar testes

```bash
python -m unittest discover -s tests
```

ou:

```bash
py -m unittest discover -s tests
```

## Estrutura de pastas

```text
atendimento/
  cli.py         Interface de terminal
  models.py      Entidades do sistema
  reports.py     Relatorios e exportacao CSV
  service.py     Regras de negocio
  storage.py     Persistencia JSON
  structures.py  Filas, pilha, lista encadeada, busca e ordenacao
data/
  sample_state.json Dados de exemplo
tests/
  test_service.py Testes unitarios basicos
RELATORIO.md     Explicacao de estruturas, Big-O e escolhas
requirements.txt Dependencias externas
```

## Dados

Por padrao, o sistema grava em `data/state.json`. Para usar os dados de exemplo,
copie o conteudo de `data/sample_state.json` para `data/state.json`.

## Regras principais

- Cliente prioridade sempre fica na frente, mas a ordem de chegada entre
  prioridades iguais e preservada.
- Atendente so atende um cliente por vez.
- Nao e permitido finalizar atendimento se o atendente nao esta ocupado.
- Nao e permitido abrir dois atendimentos simultaneos para o mesmo cliente.
- Nao e permitido remover cliente com atendimento em aberto.

## Qualidade

- Codigo modularizado por responsabilidade.
- Tratamento de erros de entrada na interface.
- Persistencia em JSON.
- Logs em `data/operations.log`.
- Testes unitarios cobrindo filas, prioridade, busca, desfazer, remocao e
  relatorios.
