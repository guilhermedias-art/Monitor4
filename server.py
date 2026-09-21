import socket
import sys
import psutil
import time
from threading import Thread, Event, Semaphore
import queue
import asyncio
import threading


HOST = '127.0.0.1'
PORT = 4998
NUM_BYTES = 1024

if len(sys.argv) < 2:
    print("Utilize: python server.py <limite_clientes>\nUtilizando 5 clientes como limite padrão")
    MAX_CLIENTES = 5
else:
    MAX_CLIENTES = int(sys.argv[1])

semaforo_clientes = Semaphore(MAX_CLIENTES)
clientes=[]
handlers_clientes = []
lock_clientes = threading.Lock()
def decodificar_mensagem(conn,fila_msg,threads_monitores,encerrar_cliente):
    try:
        tempo_formatado = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        msg = f"{tempo_formatado}: CONECTADO!!\n"
        number = 0
        fila_msg.put(msg)
        while True:
            dados = conn.recv(NUM_BYTES)
            if not dados:
                msg = f"Cliente desconectou do servidor inesperadamente\n"
                fila_msg.put(msg)
                break

            mensagem_decodificada = dados.decode("utf-8")

            if(mensagem_decodificada.upper() == 'LIST'):
                listar_monitores(fila_msg,threads_monitores)
                listar_clientes()
                continue

            elif(mensagem_decodificada.upper() == 'EXIT'):

                for monitor in threads_monitores.values():
                    monitor["evento"].set()

                threads_monitores.clear()
                msg = f'Voce encerrou a conexão com o servidor\n'
                fila_msg.put(msg)
                break

            elif ">" not in mensagem_decodificada:
                msg = f"Digite uma mensagem válida!"
                fila_msg.put(msg)
                continue

            palavra, arg = mensagem_decodificada.split(">", 1)

            palavra = palavra.strip()
            arg = arg.strip()

            if palavra.upper() in ['CPU', 'MEM', 'MEMORIA']:
                if not arg.isdigit() or int(arg) <= 0:
                    msg = "Digite um período válido!"
                    fila_msg.put(msg)
                    continue

            if(palavra.upper() == 'CPU'):
                msg = f"Comando requisitado: CPU {arg}"
                fila_msg.put(msg)

                nome = f"Monitor {number}"
                number = number + 1

                evento_parar = Event()

                thread_cpu = Thread(
                    target=monitoramento,
                    args=(nome, evento_parar, palavra, arg,fila_msg,threads_monitores),
                    daemon=True
                )

                threads_monitores[nome] = {
                    "thread": thread_cpu,
                    "evento": evento_parar,
                    "tipo": "CPU",
                    "intervalo": arg
                }

                thread_cpu.start()

            elif palavra.upper() in ['MEM', 'MEMORIA']:
                msg = f"Comando requisitado: MEM {arg}"
                fila_msg.put(msg)
                nome = f"Monitor {number}"
                number = number + 1
                evento_parar = Event()

                thread_mem = Thread(
                    target=monitoramento,
                    args=(nome, evento_parar, palavra, arg,fila_msg,threads_monitores),
                    daemon=True
                )

                threads_monitores[nome] = {
                    "thread": thread_mem,
                    "evento": evento_parar,
                    "tipo": "MEM",
                    "intervalo": arg
                }

                thread_mem.start()

            elif(palavra.upper() == 'QUIT'):

                if arg in threads_monitores:

                    threads_monitores[arg]["evento"].set()

                    msg = f"{arg} encerrado"
                    fila_msg.put(msg)

                    del threads_monitores[arg]
                else:
                    msg = f"Monitor não encontrado\n"
                    fila_msg.put(msg)


            else:
                msg = f"Digite uma mensagem válida!\n"
                fila_msg.put(msg)

    except Exception as e:
            msg = f"Erro no armazenamento de dados: {e}\n"
            fila_msg.put(msg)
    finally:
            for monitor in threads_monitores.values():
                monitor["evento"].set()
            threads_monitores.clear()
            fila_msg.put("EXIT")

def listar_monitores(fila_msg,threads_monitores):
    msg = "\n--- Threads Ativas Atualmente ---\n"
    fila_msg.put(msg)

    lista_nomes = list(threads_monitores.keys())

    if not lista_nomes:
        msg = "Nenhum monitor ativo\n"
        fila_msg.put(msg)
        return

    quantidade_ativos = 0

    for indice, nome in enumerate(lista_nomes, start=1):
        monitor = threads_monitores[nome]

        if monitor["thread"].is_alive():
            quantidade_ativos += 1

            msg = f"{indice}. {nome} - Tipo: {monitor['tipo']} - Intervalo: {monitor['intervalo']} segundos\n"
            fila_msg.put(msg)

    msg = f"\nTotal de monitores ativos: {quantidade_ativos}\n"
    fila_msg.put(msg)

def monitoramento(nome, parada, palavra, arg,fila_msg,threads_monitores):
    palavra = palavra.upper()

    while not parada.is_set():

        if (palavra == "CPU"):
            cpu = psutil.cpu_percent(interval=0.1)
            mensagem = (f'{nome} (CPU) em % = {cpu}')

        elif palavra in ["MEM", "MEMORIA"]:
            memoria = psutil.virtual_memory().percent
            mensagem = (f'{nome}: (RAM) em % = {memoria}')

        fila_msg.put(mensagem)
        print(mensagem)

        parada.wait(int(arg))
        

def enviar_dados(conn,fila_msg,encerrar_cliente):
    while not encerrar_cliente.is_set():
        try:
            msg = fila_msg.get(timeout=0.7)
            conn.sendall(msg.encode('utf-8'))
            if(msg.upper() == "EXIT"):
                print("Envio de dados encerrado\n")
                break
        except queue.Empty:
            continue
        except Exception as e:
            print(f"Envio de dados encerrado{e}\n")
            break

def aceitar_cliente(conn,endereço):
    cliente = None
    vaga_aberta = semaforo_clientes.acquire(blocking=False)
    
    if not vaga_aberta:
        msg_erro = "LIMITE DE CONEXOES ATINGIDO. Tente novamente mais tarde.\n"
        conn.sendall(msg_erro.encode('utf-8'))
        conn.close()
        return

    ativos = MAX_CLIENTES - semaforo_clientes._value
    print(f"Usuário {endereço} conectado. Clientes ativos: {ativos}/{MAX_CLIENTES}\n")

    try:
        print('Cliente conectado no :', endereço)
        fila_msg = queue.Queue()
        threads_monitores = {}
        encerrar_cliente = threading.Event()

        cliente = {
        "endereco": endereço,
        "conexao": conn,
        "thread": threading.current_thread(),
        "estado": "ATIVO",
        "fila_msg": fila_msg,
        "threads_monitores": threads_monitores,
        "encerrar": encerrar_cliente
    }

        with lock_clientes:
            clientes.append(cliente)


        msg1 = "Menu de Comandos:\n" \
                    "Listar Monitores = LIST\n" \
                    "Monitorar CPU = CPU>(tempo)\n" \
                    "Monitorar Memoria = MEM>(tempo)\n" \
                    "Terminar monitor = QUIT>(monitor)\n" \
                    "Encerrar comunicação com servidor = EXIT\n" \
    
        print(msg1)
        fila_msg.put(msg1)

        cliente["threads"] = {
        "thread1": None,
        "thread2": None,
        "monitores": []
    }

        thread1 = Thread(target=decodificar_mensagem, args=(conn,fila_msg,threads_monitores,encerrar_cliente),daemon=True)
        thread2 = Thread(target=enviar_dados, args=(conn, fila_msg,encerrar_cliente,),daemon = True)

        cliente["threads"]["thread1"] = thread1
        cliente["threads"]["thread2"] = thread2  
        
        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()

    except Exception:
        print(f"Cliente ainda conectado no endereço {endereço}")
    finally:
        for monitor in threads_monitores.values():
            monitor['evento'].set()
        
        encerrar_cliente.set()
        semaforo_clientes.release()
        conn.close()
        clientes_restantes = MAX_CLIENTES - semaforo_clientes._value
        print(f"Usuário {endereço} desconectado! Clientes ativos: {clientes_restantes}/{MAX_CLIENTES}")

        with lock_clientes:
            if cliente is not None:
                cliente["estado"] = "DESCONECTADO"
                clientes.remove(cliente)
        listar_clientes()


def listar_clientes():
    with lock_clientes:
        if not clientes:
            print("Nenhum cliente conectado.")
            return

        print("\n--- Clientes Registrados ---")

        for indice, cliente in enumerate(clientes, start=1):
            print(
                f"{indice} - "
                f"Endereço: {cliente['endereco']} | "
                f"Estado: {cliente['estado']} | "
                f"Thread: {cliente['thread'].name}"
            )

            if cliente["estado"] == "ATIVO":
                if cliente["threads_monitores"]:
                    for nome, monitor in cliente["threads_monitores"].items():
                        print(
                            f"    {nome} - "
                            f"Tipo: {monitor['tipo']} | "
                            f"Intervalo: {monitor['intervalo']} segundos"
                        )
                else:
                    print("Nenhum monitor ativo")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind((HOST,PORT))
print("Servidor Iniciado!\n")
server.listen(5)

while True:
    try:
        conexao, endereço = server.accept()
        thread3 = Thread(target = aceitar_cliente, args = (conexao,endereço,), daemon = True)
        with lock_clientes:
            handlers_clientes.append(thread3)

        thread3.start()

    except KeyboardInterrupt:
        print("\nServidor finalizado pelo operador.")
        server.close()
        sys.exit(0)

