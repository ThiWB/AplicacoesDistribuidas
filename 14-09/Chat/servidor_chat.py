import socket
import threading
import sys

HOST = sys.argv[1] if len(sys.argv) > 1 else "0.0.0.0"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 5000

clientes = {}
lock = threading.Lock()

servidor_no_chat = True
servidor_socket = None


def enviar(socket_cliente, mensagem):
    try:
        socket_cliente.sendall((mensagem + "\n").encode("utf-8"))
    except:
        pass


def broadcast(mensagem, ignorar=None):
    with lock:
        lista = list(clientes.values())

    for cliente in lista:
        if cliente["socket"] != ignorar:
            enviar(cliente["socket"], mensagem)


def lista_usuarios():
    with lock:
        if not clientes:
            return "Nenhum usuário conectado."

        resultado = ["Usuários conectados:"]

        for cliente in clientes.values():
            status = "online" if cliente["no_chat"] else "fora do chat"

            resultado.append(
                f"- {cliente['nickname']} "
                f"({cliente['endereco'][0]}) - {status}"
            )

        return "\n".join(resultado)


def ajuda():
    return """
========== AJUDA ==========
ajuda
    Mostra esta ajuda.

usuarios
    Mostra os usuários conectados.

sair
    Sai do chat.

entrar
    Entra novamente no chat.

kick <nickname>
    Expulsa um usuário.

encerrar
    Encerra o servidor e desconecta todos.
===========================
"""


def remover_cliente(socket_cliente):
    with lock:
        if socket_cliente in clientes:
            cliente = clientes.pop(socket_cliente)
        else:
            cliente = None

    if cliente:
        try:
            socket_cliente.close()
        except:
            pass


def processar_cliente(socket_cliente, endereco):
    global servidor_no_chat

    nickname = None

    try:
        enviar(socket_cliente, "Digite seu nickname:")

        dados = socket_cliente.recv(1024)

        if not dados:
            return

        nickname = dados.decode("utf-8").strip()

        if not nickname:
            nickname = f"Usuario_{endereco[1]}"

        with lock:
            clientes[socket_cliente] = {
                "socket": socket_cliente,
                "nickname": nickname,
                "endereco": endereco,
                "no_chat": True
            }

        enviar(
            socket_cliente,
            f"Bem-vindo, {nickname}! Digite 'ajuda' para ver os comandos."
        )

        broadcast(
            f"[SERVIDOR] {nickname} entrou no chat.",
            ignorar=socket_cliente
        )

        while True:
            dados = socket_cliente.recv(1024)

            if not dados:
                break

            mensagem = dados.decode("utf-8").strip()

            if not mensagem:
                continue

            comando = mensagem.lower()

            # AJUDA
            if comando == "ajuda":
                enviar(socket_cliente, ajuda())

            # USUARIOS
            elif comando == "usuarios":
                enviar(socket_cliente, lista_usuarios())

            # SAIR
            elif comando == "sair":
                with lock:
                    if socket_cliente in clientes:
                        clientes[socket_cliente]["no_chat"] = False

                enviar(socket_cliente, "Você saiu do chat.")
                broadcast(
                    f"[SERVIDOR] {nickname} saiu do chat.",
                    ignorar=socket_cliente
                )

            # ENTRAR
            elif comando == "entrar":
                with lock:
                    if socket_cliente in clientes:
                        clientes[socket_cliente]["no_chat"] = True

                enviar(socket_cliente, "Você entrou novamente no chat.")

                broadcast(
                    f"[SERVIDOR] {nickname} entrou novamente no chat.",
                    ignorar=socket_cliente
                )

            # KICK
            elif comando.startswith("kick "):
                nome_expulsar = mensagem[5:].strip()

                encontrado = None

                with lock:
                    for sock, cliente in clientes.items():
                        if cliente["nickname"].lower() == nome_expulsar.lower():
                            encontrado = (sock, cliente)
                            break

                if encontrado:
                    sock_expulso, cliente_expulso = encontrado

                    enviar(
                        sock_expulso,
                        "[SERVIDOR] Você foi expulso do chat."
                    )

                    broadcast(
                        f"[SERVIDOR] {cliente_expulso['nickname']} "
                        f"foi expulso do chat.",
                        ignorar=sock_expulso
                    )

                    remover_cliente(sock_expulso)

                else:
                    enviar(
                        socket_cliente,
                        f"Usuário '{nome_expulsar}' não encontrado."
                    )

            # ENCERRAR
            elif comando == "encerrar":
                enviar(
                    socket_cliente,
                    "[SERVIDOR] Encerrando o servidor..."
                )
                break

            # MENSAGEM NORMAL
            else:
                with lock:
                    ativo = (
                        socket_cliente in clientes
                        and clientes[socket_cliente]["no_chat"]
                    )

                if ativo:
                    mensagem_formatada = (
                        f"[{nickname} - {endereco[0]}]: {mensagem}"
                    )

                    broadcast(
                        mensagem_formatada,
                        ignorar=socket_cliente
                    )

    except ConnectionResetError:
        pass

    except Exception as e:
        print(f"Erro com {endereco}: {e}")

    finally:
        remover_cliente(socket_cliente)

        if nickname:
            broadcast(
                f"[SERVIDOR] {nickname} desconectou."
            )


def entrada_servidor():
    """
    Permite que o próprio servidor participe do chat.
    """

    global servidor_no_chat

    while True:
        try:
            mensagem = input("[SERVIDOR]: ").strip()

            if mensagem.lower() == "sair":
                servidor_no_chat = False

                broadcast("[SERVIDOR] saiu do chat.")
                print("[*] Servidor saiu do chat.")

            elif mensagem.lower() == "entrar":
                servidor_no_chat = True

                broadcast("[SERVIDOR] entrou novamente no chat.")
                print("[*] Servidor entrou no chat.")

            elif mensagem.lower() == "usuarios":
                print(lista_usuarios())

            elif mensagem.lower() == "ajuda":
                print(ajuda())

            elif mensagem.lower() == "encerrar":
                broadcast("[SERVIDOR] Chat encerrado.")

                with lock:
                    lista = list(clientes.keys())

                for cliente in lista:
                    try:
                        cliente.close()
                    except:
                        pass

                break

            elif servidor_no_chat:
                broadcast(f"[SERVIDOR - HOST]: {mensagem}")

        except EOFError:
            break


servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

servidor.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

servidor.bind((HOST, PORT))
servidor.listen(10)

print(
    f"[*] Servidor de chat rodando em "
    f"{HOST}:{PORT}"
)

thread_servidor = threading.Thread(
    target=entrada_servidor,
    daemon=True
)

thread_servidor.start()

try:
    while True:
        socket_cliente, endereco = servidor.accept()

        print(
            f"[+] Nova conexão: "
            f"{endereco[0]}:{endereco[1]}"
        )

        thread = threading.Thread(
            target=processar_cliente,
            args=(socket_cliente, endereco),
            daemon=True
        )

        thread.start()

except KeyboardInterrupt:
    print("\n[*] Servidor interrompido.")

finally:
    servidor.close()