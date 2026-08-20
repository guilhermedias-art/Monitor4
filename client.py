import socket
from threading import Thread

HOST = '127.0.0.1'
PORT = 4998
NUM_BYTES = 1024

cliente = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
cliente.connect((HOST,PORT))

def envio_d_dados(client) :
    print("MENU:\n" \
    "Monitorar CPU -> CPU<(tempo)\n" \
    "Monitorar Memoria -> MEM<(tempo)\n" \
    "Sair -> quit\n" \
    "Terminar -> exit\n")

    while True:
        mensagem = input("")
        client.sendall(mensagem.encode('utf-8'))


def exibir_msg(client):
        while True:
            dados_p_decodificar = client.recv(NUM_BYTES)
            if not dados_p_decodificar :
                print("A mensagem que o usuário digitou não conseguiu ser lida")
                quit()
            mensagem_decodificada = dados_p_decodificar.decode('utf-8')
            print(mensagem_decodificada)


thread1 = Thread(target =envio_d_dados, args=(cliente,),daemon = True)
thread2 = Thread(target =exibir_msg, args=(cliente,),daemon= True) 

thread1.start()
thread2.start()

thread1.join()
thread2.join()




