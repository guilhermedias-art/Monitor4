import socket
import sys
import psutil
import time

HOST = "127.0.0.1"
PORT = 1080
NUM_BYTES = 1024

tempo_atual = time.time()
 
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

server.listen(1)

connection, address = server.accept()

def input_dados(connection) :
    while True:
        dados = connection.recv(NUM_BYTES)
        if not dados:
            print("Cliente não conseguiu se conectar")
            break
        msg = dados.decode('utf-8')
        print('{tempo_atual} ' > CONECTADO)





def enviar_dados() :
    cpu = psutil.cpu_percent()
    memoria = psutil.virtual_memory().percent 
    


