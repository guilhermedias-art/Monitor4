import socket
import sys
import psutil
import time
from threading import Thread, Event
import queue

HOST = '127.0.0.1'
PORT = 4998
NUM_BYTES = 1024

tempo_formatado = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

fila_msg = queue.Queue()
threads_monitores = {}

def decodificar_mensagem(conn):
    try:

        tempo_formatado = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        msg = f"{tempo_formatado}: CONECTADO!!\n"
        number = 0
        fila_msg.put(msg)

        while True:
            dados = conn.recv(NUM_BYTES)
            if not dados:

                for monitor in threads_monitores.values():
                    monitor["evento"].set()

                threads_monitores.clear()
                fila_msg.put("EXIT")
                break

            mensagem_decodificada = dados.decode("utf-8")

            if(mensagem_decodificada.upper() == 'LIST'):
                listar_monitores()
                continue

            elif(mensagem_decodificada.upper() == 'EXIT'):

                for monitor in threads_monitores.values():
                    monitor["evento"].set()

                threads_monitores.clear()
                msg = f'Voce encerrou a conexão com o servidor'
                fila_msg.put(msg)
                msg = "EXIT"
                fila_msg.put(msg)
                break

            elif ">" not in mensagem_decodificada:
                msg = f"Digite uma mensagem válida!"
                fila_msg.put(msg)
                continue

            palavra, arg = mensagem_decodificada.split(">", 1)

            palavra = palavra.strip()
            arg = arg.strip()

            if palavra.upper() in ['CPU', 'MEM', 'MEMORIA']:
                if not arg.isdigit() or int(arg) <= 0:
                    msg = "Digite um período válido!"
                    fila_msg.put(msg)
                    continue

            if(palavra.upper() == 'CPU'):
                msg = f"Comando requisitado: CPU {arg}"
                fila_msg.put(msg)

                nome = f"Monitor {number}"
                number = number + 1

                evento_parar = Event()

                thread_cpu = Thread(
                    target=monitoramento,
                    args=(nome, evento_parar, palavra, arg)
                )

                threads_monitores[nome] = {
                    "thread": thread_cpu,
                    "evento": evento_parar,
                    "tipo": "CPU",
                    "intervalo": arg
                }

                thread_cpu.start()

            elif palavra.upper() in ['MEM', 'MEMORIA']:
                msg = f"Comando requisitado: MEM {arg}"
                fila_msg.put(msg)
                nome = f"Monitor {number}"
                number = number + 1
                evento_parar = Event()

                thread_mem = Thread(
                    target=monitoramento,
                    args=(nome, evento_parar, palavra, arg)
                )

                threads_monitores[nome] = {
                    "thread": thread_mem,
                    "evento": evento_parar,
                    "tipo": "MEM",
                    "intervalo": arg
                }

                thread_mem.start()

            elif(palavra.upper() == 'QUIT'):

                if arg in threads_monitores:

                    threads_monitores[arg]["evento"].set()

                    msg = f"{arg} encerrado"
                    fila_msg.put(msg)

                    del threads_monitores[arg]

                else:

                    msg = f"Monitor não encontrado"
                    fila_msg.put(msg)

            else:
                msg = f"Digite uma mensagem válida!"
                fila_msg.put(msg)

    except Exception as e:
            msg = f"Erro no armazenamento de dados: {e}"
            fila_msg.put(msg)

            for monitor in threads_monitores.values():
                monitor["evento"].set()

            threads_monitores.clear()
            fila_msg.put("EXIT")

def listar_monitores():
    msg = "\n--- Threads Ativas Atualmente ---\n"
    fila_msg.put(msg)

    lista_nomes = list(threads_monitores.keys())

    if not lista_nomes:
        msg = "Nenhum monitor ativo\n"
        fila_msg.put(msg)
        return

    quantidade_ativos = 0

    for indice, nome in enumerate(lista_nomes, start=1):
        monitor = threads_monitores[nome]

        if monitor["thread"].is_alive():
            quantidade_ativos += 1

            msg = f"{indice}. {nome} - Tipo: {monitor['tipo']} - Intervalo: {monitor['intervalo']} segundos\n"
            fila_msg.put(msg)

    msg = f"\nTotal de monitores ativos: {quantidade_ativos}\n"
    fila_msg.put(msg)

def monitoramento(nome, parada, palavra, arg):
    palavra = palavra.upper()

    while not parada.is_set():

        if (palavra == "CPU"):
            cpu = psutil.cpu_percent(interval=1)
            mensagem = (f'{nome} (CPU) em % = {cpu}')

        elif palavra in ["MEM", "MEMORIA"]:
            memoria = psutil.virtual_memory().percent
            mensagem = (f'{nome}: (RAM) em % = {memoria}')

        fila_msg.put(mensagem)
        print(mensagem)

        parada.wait(int(arg))


def enviar_dados(conn, ):
    while True:
        try:
            msg = fila_msg.get()

            if(msg.upper() == "EXIT"):
                finish = True
                conn.sendall(msg.encode('utf-8'))
                print("Envio de dados encerrado")
                break

            conn.sendall(msg.encode('utf-8'))
            
        except (Exception):
            break

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind((HOST,PORT))
print("Servidor Iniciado!\n")
server.listen(1)

while True:
    try:
        conexao, endereço = server.accept()
        print('Serviço conectado no :', endereço)

        msg = "Menu de Comandos:\n" \
            "Listar Monitores = LIST\n" \
            "Monitorar CPU = CPU>(tempo)\n" \
            "Monitorar Memoria = MEM>(tempo)\n" \
            "Terminar monitor = QUIT>(monitor)\n" \
            "Terminar = exit\n"

        thread1 = Thread(target=decodificar_mensagem, args=(conexao,),daemon=True)
        thread2 = Thread(target=enviar_dados, args=(conexao, ),daemon = True)

        thread1.start()
        thread2.start()

        fila_msg.put(msg)

        thread1.join()
        thread2.join()

        conexao.close()
        print("Usuário desconectado!")

    except KeyboardInterrupt:
        print("\nServidor finalizado pelo operador.")
        server.close()
        sys.exit(0)
