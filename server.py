import socket
import sys
import psutil
import time

HOST = '127.0.0.1'
PORT = 5000
NUM_BYTES = 1024

tempo_atual = time.time()
 
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST,PORT))

server.listen(1)

conexao, endereço = server.accept()
with conexao:
    print('Conectado no :', endereço)
    while True:
         dados = conexao.recv(NUM_BYTES)
         if not dados:
            conexao.sendall(dados)

        


def input_dados(conexao) :
    while True:
        if not dados:
            print("Cliente não conseguiu se conectar")
            break
        msg = dados.decode('utf-8')
        print('{tempo_atual} ' > CONECTADO)
        print('Serviço conectado em {HOST}{PORT}')





def enviar_dados() :
    cpu = psutil.cpu_percent()
    memoria = psutil.virtual_memory().percent 
    print('Uso de CPU em % = {cpu}')
    print('Uso de RAM em % = {memoria}')


