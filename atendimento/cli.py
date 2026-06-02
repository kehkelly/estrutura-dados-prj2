from atendimento.reports import (
    exportar_csv,
    tempo_medio,
    top_clientes_mais_atendidos,
)
from atendimento.service import AtendimentoService


def ler_int(mensagem: str) -> int:
    while True:
        valor = input(mensagem).strip()
        try:
            return int(valor)
        except ValueError:
            print("Digite um numero inteiro valido.")


def ler_bool(mensagem: str) -> bool:
    while True:
        valor = input(mensagem).strip().lower()
        if valor in {"s", "sim", "1"}:
            return True
        if valor in {"n", "nao", "não", "0"}:
            return False
        print("Responda com s/n.")


def mostrar_menu() -> None:
    print("\nSistema de Atendimento")
    print("1 - Cadastrar cliente")
    print("2 - Cadastrar atendente")
    print("3 - Abrir atendimento")
    print("4 - Chamar proximo")
    print("5 - Finalizar atendimento")
    print("6 - Historico por cliente")
    print("7 - Desfazer ultima finalizacao")
    print("8 - Remover clientes inativos")
    print("9 - Relatorios")
    print("10 - Buscar cliente por id")
    print("11 - Ver filas")
    print("0 - Sair")


def menu_relatorios(service: AtendimentoService) -> None:
    print(f"Tempo medio: {tempo_medio(service):.2f} minutos")
    print("Top 5 clientes mais atendidos:")
    for cliente_id, nome, total in top_clientes_mais_atendidos(service):
        print(f"- {cliente_id} | {nome}: {total} atendimento(s)")
    alertas = service.alertas_espera_alta()
    if alertas:
        print("Alertas de espera alta:")
        for ticket in alertas:
            print(f"- Cliente {ticket.cliente_id} espera desde {ticket.aberto_em}")
    caminho = exportar_csv(service)
    print(f"CSV exportado para {caminho}")


def executar_opcao(service: AtendimentoService, opcao: str) -> bool:
    try:
        if opcao == "1":
            cliente_id = ler_int("Id: ")
            nome = input("Nome: ")
            telefone = input("Telefone: ")
            prioridade = ler_bool("Prioridade? (s/n): ")
            cliente = service.cadastrar_cliente(
                cliente_id,
                nome,
                telefone,
                prioridade,
            )
            print(f"Cliente cadastrado: {cliente}")
        elif opcao == "2":
            atendente_id = ler_int("Id: ")
            nome = input("Nome: ")
            atendente = service.cadastrar_atendente(atendente_id, nome)
            print(f"Atendente cadastrado: {atendente}")
        elif opcao == "3":
            ticket = service.abrir_atendimento(ler_int("Id do cliente: "))
            print(f"Atendimento aberto: {ticket}")
        elif opcao == "4":
            ticket = service.chamar_proximo(ler_int("Id do atendente: "))
            print(f"Cliente chamado: {ticket.cliente_id}")
        elif opcao == "5":
            atendente_id = ler_int("Id do atendente: ")
            duracao = ler_int("Duracao em minutos: ")
            atendimento = service.finalizar_atendimento(atendente_id, duracao)
            print(f"Atendimento finalizado: {atendimento}")
        elif opcao == "6":
            cliente_id = ler_int("Id do cliente: ")
            historico = service.historico_por_cliente(cliente_id)
            if not historico:
                print("Nenhum atendimento encontrado.")
            for item in historico:
                print(item)
        elif opcao == "7":
            atendimento = service.desfazer_ultima_finalizacao()
            print(f"Finalizacao desfeita: {atendimento}")
        elif opcao == "8":
            removidos = service.remover_clientes_inativos()
            print(f"Clientes inativados: {len(removidos)}")
        elif opcao == "9":
            menu_relatorios(service)
        elif opcao == "10":
            cliente = service.buscar_cliente(ler_int("Id do cliente: "))
            print(cliente if cliente else "Cliente nao encontrado.")
        elif opcao == "11":
            filas = service.listar_filas()
            print("Prioridade:")
            for ticket in filas["prioridade"]:
                print(f"- Cliente {ticket.cliente_id} desde {ticket.aberto_em}")
            print("Comum:")
            for ticket in filas["comum"]:
                print(f"- Cliente {ticket.cliente_id} desde {ticket.aberto_em}")
        elif opcao == "0":
            return False
        else:
            print("Opcao invalida.")
    except ValueError as erro:
        print(f"Erro: {erro}")
    return True


def main() -> None:
    service = AtendimentoService()
    continuar = True
    while continuar:
        mostrar_menu()
        continuar = executar_opcao(service, input("Opcao: ").strip())

