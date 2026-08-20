import socket
import sys
import psutil
import time
from threading import Thread
import queue

HOST = '127.0.0.1'
PORT = 4998
NUM_BYTES = 1024

tempo_formatado = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

fila_msg = queue.Queue()

def decodificar_mensagem(conn):
    # Implementar aqui a escolha do comando
    try:
        msg = f"{tempo_formatado} -> CONECTADO"
        fila_msg.put(msg)

        while True:
            dados = conn.recv(NUM_BYTES)

            if not dados:
                msg= "Cliente não conseguiu se conectar"
                fila_msg.append(msg)
                break

            mensagem_decodificada = dados.decode("utf-8")

            palavra, arg = mensagem_decodificada.split("<")

            if(palavra.upper() == 'CPU'):
                msg = f"Comando requisitado: CPU {arg}"
                fila_msg.put(msg)
                thread_mem = Thread(target=monitoramento, args=(palavra, arg))
                thread_mem.start()
                
            elif(palavra.upper() == 'MEM'):
                msg = f"Comando requisitado: MEM {arg}"
                fila_msg.put(msg)
                thread_mem = Thread(target=monitoramento, args=(palavra, arg))
                thread_mem.start()

            elif(palavra.upper() == 'QUIT'):
                msg = f"Comando requisitado: Quit {arg}"
                fila_msg.put(msg)

            elif(palavra.upper() == 'EXIT'):
                msg = f'Voce encerrou a conexão com o servidor'
                fila_msg.put(msg)
                break

            else:
                msg = f"Digite uma mensagem válida!"
                fila_msg.put(msg)

    except Exception as e:
            msg = f"Erro no armazenamento de dados: {e}"


def monitoramento(palavra, arg):
    palavra = palavra.upper()
    mensagem = ""
    if (palavra == "CPU"):
        cpu = psutil.cpu_percent()
        mensagem = (f'Uso de CPU em % = {cpu}')
    elif (palavra == "MEM"):
        memoria = psutil.virtual_memory().percent
        mensagem = (f'Uso de RAM em % = {memoria}')
    
    while True:
        fila_msg.put(mensagem)
        print(mensagem)
        time.sleep(int(arg))

def enviar_dados(conn, ):
    while True:
            msg = fila_msg.get()
            conn.sendall(msg.encode('utf-8'))

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind((HOST,PORT))
print("Servidor Iniciado!\n")
server.listen(1)

while True:
    conexao, endereço = server.accept()
    print('Serviço conectado no :', endereço)

    thread1 = Thread(target=decodificar_mensagem, args=(conexao,),daemon=True)
    thread2 = Thread(target=enviar_dados, args=(conexao, ),daemon = True)

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()
