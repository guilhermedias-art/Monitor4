import socket
import sys
from threading import Thread

HOST = '127.0.0.1'
PORT = 4998
NUM_BYTES = 1024

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    cliente.connect((HOST, PORT))
except Exception as e:
    print(f"Não foi possível conectar ao servidor: {e}")
    sys.exit(1)

def envio_d_dados(client):
    while True:
        try:
            mensagem = input("")
            if mensagem:
                client.sendall(mensagem.encode('utf-8'))
        except (BufferError, ConnectionResetError, BrokenPipeError):
            break

def exibir_msg(client):
    while True:
        try:
            dados_p_decodificar = client.recv(NUM_BYTES)
            if not dados_p_decodificar:
                print("\nConexão encerrada pelo servidor.")
                break

            mensagem_decodificada = dados_p_decodificar.decode('utf-8').strip()
            print(mensagem_decodificada)


            if mensagem_decodificada == "EXIT":
                print("\nSaindo do programa")
                client.close()
                break

        except Exception:
            break


    client.close()
    sys.exit(0)

# Criando threads
thread1 = Thread(target=envio_d_dados, args=(cliente,), daemon=True)
thread2 = Thread(target=exibir_msg, args=(cliente,), daemon=True)

thread1.start()
thread2.start()


thread2.join()