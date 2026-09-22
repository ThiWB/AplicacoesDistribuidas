import socket
import threading
import sys

HOST = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 5000


def receber_mensagens(cliente):
    while True:
        try:
            dados = cliente.recv(4096)

            if not dados:
                print("\n[*] Servidor desconectado.")
                break

            mensagem = dados.decode("utf-8")

            print("\n" + mensagem)
            print("[Você]: ", end="", flush=True)

        except:
            break


cliente = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

try:
    cliente.connect((HOST, PORT))

    resposta = cliente.recv(1024)
    print(resposta.decode("utf-8"))

    nickname = input("Nickname: ")

    cliente.sendall(
        nickname.encode("utf-8")
    )

    thread = threading.Thread(
        target=receber_mensagens,
        args=(cliente,),
        daemon=True
    )

    thread.start()

    print(
        "\nConectado ao chat!"
        "\nDigite 'ajuda' para ver os comandos."
    )

    while True:
        mensagem = input("[Você]: ").strip()

        if not mensagem:
            continue

        cliente.sendall(
            mensagem.encode("utf-8")
        )

        if mensagem.lower() == "encerrar":
            break

except ConnectionRefusedError:
    print("[-] Não foi possível conectar ao servidor.")

except KeyboardInterrupt:
    print("\n[*] Cliente encerrado.")

finally:
    cliente.close()