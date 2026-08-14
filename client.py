import socket
import sys
import psutil
import time


HOST = '127.0.0.1'
PORT =  5000
NUM_BYTES = 1024

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

def input_usuario(client):
    while True:
        mensagem = input(">")
        client.sendall(mensagem.encode('utf-8'))
        resposta = client.recv(NUM_BYTES)




        


    







    










