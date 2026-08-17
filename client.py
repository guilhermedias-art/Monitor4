import socket
import sys
import psutil
import time


HOST = '127.0.0.1'
PORT = 4998
NUM_BYTES = 1024

cliente = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

cliente.connect((HOST,PORT))


def envio_d_dados(client) :
    while True:
        mensagem = input("CPU-5<  ")
        client.sendall(mensagem.encode('utf-8'))


def exibir_msg(client):
    while True:
        dados_p_decodificar = client.recv(NUM_BYTES)
        if not dados_p_decodificar :
            print("A mensagem que o usuário digitou não conseguiu ser lida")
            quit()
        mensagem_decodificada = dados_p_decodificar.decode('utf-8')
        print(mensagem_decodificada)


try :
    envio_d_dados(cliente)
    exibir_msg(cliente)

        

except SystemError :
    print("Tente Novamente!")


finally:
    quit()


