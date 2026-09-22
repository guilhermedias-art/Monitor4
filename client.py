import socket
import sys
from threading import Thread,Event

HOST = '127.0.0.1'
PORT = 4998
NUM_BYTES = 1024

encerrar_cliente = Event()
cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    cliente.connect((HOST, PORT))
except Exception as e:
    print(f"Não foi possível conectar ao servidor")
    sys.exit(1)

def envio_d_dados(client,encerrar_cliente):
    while not encerrar_cliente.is_set():
        try:
            mensagem = input("")
            if mensagem: 
                try:
                    client.sendall(mensagem.encode('utf-8'))
                except(OSError, BrokenPipeError):
                    print("\nTentativa de conexão falha, tente novamente!")
            if mensagem.strip().upper() == "EXIT":
                break
        except (ConnectionResetError, OSError, BrokenPipeError, EOFError, KeyboardInterrupt):
            print("\nConexão finalizada!")
            break

def exibir_msg(client,encerrar_cliente):
    while not encerrar_cliente.is_set():
        try:
            dados_p_decodificar = client.recv(NUM_BYTES)

            if not dados_p_decodificar:
                print("\nConexão encerrada pelo servidor.")
                break

            mensagem_decodificada = dados_p_decodificar.decode('utf-8').strip()
            print(mensagem_decodificada)

            if mensagem_decodificada == "EXIT":
                print("\nSaindo do programa")
                encerrar_cliente.set()
                break

        except (ConnectionResetError, ConnectionAbortedError, OSError):
            encerrar_cliente.set()
            print("\nConexão encerrada pelo servidor.")
            break

    try:
        client.close()
    except OSError:
        pass


thread1 = Thread(target=envio_d_dados, args=(cliente,encerrar_cliente,), daemon=True)
thread2 = Thread(target=exibir_msg, args=(cliente,encerrar_cliente,), daemon=True)

thread1.start()
thread2.start()

try:
    thread2.join()
except KeyboardInterrupt:
    print("\nCliente finalizado pelo usuário.")
    sys.exit(0)

sys.exit(0)
