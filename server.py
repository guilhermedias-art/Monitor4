import socket
import sys
import psutil
import time

HOST = '127.0.0.1'
PORT = 4998
NUM_BYTES = 1024

tempo_formatado = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def decodificar_mensagem(conn):
    dados = conn.recv(NUM_BYTES)
    if not dados:
        print("Cliente não conseguiu se conectar")

    mensagem_decodificada = dados.decode("utf-8")

    if mensagem_decodificada == 'q':
        quit()

    print(mensagem_decodificada)
    

def enviar_dados(conn):

    cpu = psutil.cpu_percent()
    memoria = psutil.virtual_memory().percent 
    print(f'Uso de CPU em % = {cpu}')
    print(f'Uso de RAM em % = {memoria}')





server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST,PORT))

server.listen(1)
while True:
    conexao, endereço = server.accept()
    print('Serviço conectado no :', endereço)
    decodificar_mensagem(conexao)
    print(f"{tempo_formatado} -> CONECTADO")
    enviar_dados(conexao)











