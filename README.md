# Projeto Prático 1: Monitor do Sistema
## Disciplina: Redes de Computadores

Este projeto implementa uma aplicação de rede no modelo cliente/servidor para monitoramento remoto de recursos do sistema operacional (CPU e Memória RAM). A arquitetura foi desenvolvida utilizando Sockets em Python, Threads e estruturas de dados compartilhadas para comunicação assíncrona bidirecional, atendendo aos requisitos das Fases 1, 2 e 3 da especificação do Projeto Prático 1.

## Arquitetura do Sistema

O sistema é baseado no diagrama de fluxos especificado, dividindo as responsabilidades de rede e processamento em threads dedicadas para evitar o bloqueio da aplicação.

### Lado Cliente (`client.py`)
Ao ser executado, o cliente estabelece a conexão TCP com o servidor. A partir desse momento, ele se divide em duas threads principais:
*   **Thread 1 (Envio):** Permanece em loop infinito aguardando a entrada de comandos do usuário via teclado e transmitindo os dados codificados pela rede (socket).
*   **Thread 2 (Recepção):** Permanece em loop infinito escutando o socket. Qualquer dado recebido do servidor (mensagens do menu, confirmações ou dados de leitura de hardware) é imediatamente decodificado e impresso na tela.

### Lado Servidor (`server.py`)
O servidor aguarda conexões em uma porta específica. Ao receber um cliente, a mensagem inicial `<HORARIO> - Conectado!` e o Menu de instruções são enviados. O atendimento ao cliente é isolado em duas threads:
*   **Thread 1 (Decodificação e Controle):** Lê os pacotes da rede. É a thread responsável por atuar como orquestradora: ela interpreta os comandos do cliente e **inicia novas threads de monitoramento independentes** para cada solicitação de CPU ou Memória.
*   **Thread 2 (Transmissão de Saída):** Aguarda mensagens em uma estrutura de memória compartilhada (`queue.Queue`). Quando as threads de monitoramento produzem dados (ou o servidor gera avisos), esta thread os consome e os envia ao cliente pela rede.
*   **Threads de Monitoramento (Dinâmicas):** Criadas dinamicamente pela Thread 1 do servidor sob demanda. Elas coletam os dados de hardware utilizando a biblioteca `psutil` na periodicidade estipulada pelo usuário. O controle de encerramento destas threads é feito de forma segura utilizando flags de `threading.Event()`, evitando deadlocks e paradas abruptas.

## Funcionalidades e Comandos

O servidor interpreta os comandos enviados pelo cliente para gerenciar os monitores em tempo real. A comunicação utiliza a sintaxe `COMANDO>ARGUMENTO`.

*   `CPU>(tempo)`: Inicia uma thread para aferir a porcentagem de uso da CPU na periodicidade em segundos estipulada.
*   `MEM>(tempo)`: Inicia uma thread para aferir a porcentagem de uso da RAM na periodicidade em segundos estipulada.
*   `LIST`: Lista todas as threads de monitores ativas no momento e seus identificadores.
*   `QUIT>(nome_do_monitor)`: Envia um sinal para finalizar especificamente a thread de um monitor remoto sem afetar as demais conexões e operações.
*   `EXIT`: Solicita o encerramento de todas as threads ativas. O servidor interrompe as medições, fecha o socket e instrui o cliente a se desligar.

## Fase 2: Multi-Cliente

O servidor foi estendido para suportar múltiplos clientes simultâneos de forma isolada e segura:

*   **Controle de limite:** Um `Semaphore` limita o número de clientes simultâneos. Caso o limite seja atingido, o novo cliente recebe a mensagem `LIMITE DE CONEXOES ATINGIDO` e a conexão é encerrada de forma limpa com `shutdown()`.
*   **Isolamento por cliente:** Cada cliente possui sua própria `queue.Queue`, seu dicionário de `threads_monitores` e seu `threading.Event` de encerramento — sem compartilhamento de estado entre sessões distintas.
*   **Thread handler:** Cada cliente é atendido por uma thread dedicada (`thread3`), rastreada em `handlers_clientes`.

## Fase 3: Tratamento de Exceções e Estabilidade

O foco desta fase foi garantir que nenhum erro ou warning do interpretador seja exibido em nenhuma situação de uso:

*   **Vazamento de memória corrigido:** `handlers_clientes` é podado periodicamente com `[t for t in handlers_clientes if t.is_alive()]`, removendo threads finalizadas.
*   **Segurança de iteração:** Iterações sobre `threads_monitores` usam `list(...)` para criar snapshots, evitando `RuntimeError` por modificação de dicionário durante iteração concorrente.
*   **Exceções de socket silenciosas:** `BrokenPipeError`, `ConnectionResetError` e `OSError` são capturadas explicitamente nos loops de leitura e escrita, sem propagar tracebacks ao console.
*   **Cliente estável:** `KeyboardInterrupt` (Ctrl+C) e `EOFError` (Ctrl+D) são tratados no cliente, encerrando o processo de forma limpa.

## Como Executar

### Pré-requisitos
O servidor requer a biblioteca `psutil` instalada no ambiente Python para a extração dos dados do Sistema Operacional.
```bash
pip install psutil
```