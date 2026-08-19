import socket
import sys
import psutil
import time
from threading import Thread

HOST = '127.0.0.1'
PORT = 4998
NUM_BYTES = 1024

periodo = int(input())
tipo = int(input())

tempo_formatado = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def decodificar_mensagem(conn):
    try:
        while True:
            dados = conn.recv(NUM_BYTES)
            if not dados:
                print("Cliente não conseguiu se conectar")
                break
            print(f"{tempo_formatado} -> CONECTADO")
            mensagem_decodificada = dados.decode("utf-8")
            if mensagem_decodificada == 'q':
                print('Voce encerrou a conexão com o servidor')
                break

            print(mensagem_decodificada)
    except Exception as e:
            print("Erro no armazenamento de dados")

    

def enviar_dados(conn, tipo, periodo):
    while True:
            cpu = psutil.cpu_percent()
            memoria = psutil.virtual_memory().percent
            mensagem = (f'Uso de CPU em % = {cpu} , Uso de RAM em % = {memoria}')
            conn.sendall(mensagem.encode('utf-8'))
            time.sleep(5)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST,PORT))
print("Servidor Iniciado!\n")
server.listen(1)

while True:
    conexao, endereço = server.accept()
    print('Serviço conectado no :', endereço)

    print("MENU:\n" \
    "1. Monitorar CPU\n" \
    "2. Monitorar Memoria\n" \
    "3. Sair (quit)\n" \
    "4. Terminar\n")

    thread1 = Thread(target=decodificar_mensagem, args=(conexao,),daemon=True)
    thread2 = Thread(target=enviar_dados, args=(conexao, tipo, periodo),daemon = True)

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()
