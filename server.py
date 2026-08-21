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
        msg = f"{tempo_formatado} : CONECTADO!"
        number = 0
        fila_msg.put(msg)

        while True:
            dados = conn.recv(NUM_BYTES)
            if not dados:
                msg= "Cliente não conseguiu se conectar"
                fila_msg.put(msg)
                break

            mensagem_decodificada = dados.decode("utf-8")

            if(mensagem_decodificada.upper() == 'LIST'):
                listar_monitores()
                continue
            
            elif(mensagem_decodificada.upper() == 'QUIT'):
                # Desligar um monitor em especifico
                
                '''msg = f"Comando requisitado: Quit"
                fila_msg.put(msg)
                break
                '''
                continue

            elif(mensagem_decodificada.upper() == 'EXIT'):
                msg = f'Voce encerrou a conexão com o servidor'
                fila_msg.put(msg)
                msg = "EXIT"
                fila_msg.put(msg)
                break

            elif "<" not in mensagem_decodificada:
                msg = f"Digite uma mensagem válida!"
                fila_msg.put(msg)
                continue

            palavra, arg = mensagem_decodificada.split("<", 1)

            if(palavra.upper() == 'CPU'):
                msg = f"Comando requisitado: CPU {arg}"
                fila_msg.put(msg)
                nome = f"Monitor {number}"
                number = number + 1
                evento_parar = Event()
                thread_cpu = Thread(target=monitoramento, args=(nome, evento_parar, palavra, arg))
                threads_monitores[nome] = {"thread": thread_cpu, "evento": evento_parar}
                thread_cpu.start()

            elif(palavra.upper() == 'MEM'):
                msg = f"Comando requisitado: MEM {arg}"
                fila_msg.put(msg)
                nome = f"Monitor {number}"
                number = number + 1
                evento_parar = Event()
                thread_mem = Thread(target=monitoramento, args=(nome, evento_parar, palavra, arg))
                thread_mem.start()

            else:
                msg = f"Digite uma mensagem válida!"
                fila_msg.put(msg)

    except Exception as e:
            msg = f"Erro no armazenamento de dados: {e}"
            fila_msg.put(msg)

def listar_monitores():
    msg = "\n--- Threads Ativas Atualmente ---\n"
    fila_msg.put(msg)

    lista_nomes = list(threads_monitores.keys())

    for indice, nome in enumerate(lista_nomes, start=1):
        msg = f"[{indice}] {nome}\n"
        fila_msg.put(msg)
    

def monitoramento(nome, parada, palavra, arg):
    palavra = palavra.upper()

    while not parada.is_set():

        if (palavra == "CPU"):
            cpu = psutil.cpu_percent(interval=1)
            mensagem = (f'{nome} (CPU) em % = {cpu}')

        elif (palavra == "MEM"):
            memoria = psutil.virtual_memory().percent
            mensagem = (f'{nome}: (RAM) em % = {memoria}')

        fila_msg.put(mensagem)
        print(mensagem)

        time.sleep(int(arg))


def enviar_dados(conn, ):
    finish = False
    while not finish:
            msg = fila_msg.get()
            if(msg.upper() == "EXIT"):
                finish = True
                print("Envio de dados encerrado")
                break

            conn.sendall(msg.encode('utf-8'))

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind((HOST,PORT))
print("Servidor Iniciado!\n")
server.listen(1)

while True:
    conexao, endereço = server.accept()
    print('Serviço conectado no :', endereço)

    msg = "Menu de Comandos:\n" \
            "Listar Monitores = LIST\n" \
            "Monitorar CPU = CPU-(tempo)\n" \
            "Monitorar Memoria = MEM-(tempo)\n" \
            "Sair = quit\n" \
            "Terminar = exit\n"

    thread1 = Thread(target=decodificar_mensagem, args=(conexao,),daemon=True)
    thread2 = Thread(target=enviar_dados, args=(conexao, ),daemon = True)

    thread1.start()
    thread2.start()

    fila_msg.put(msg)

    thread1.join()
    thread2.join()