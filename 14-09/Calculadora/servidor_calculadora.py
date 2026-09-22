import sys
import socket

HOST = sys.argv[1] if len(sys.argv) > 1 else '0.0.0.0'
PORT = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(1)

print(f"[-] Servidor calculadora rodando em {HOST}:{PORT}...")

try:
    conexao, cliente_ip = server.accept()
    print(f"[+] Conectado por: {cliente_ip}")

    while True:
        dados = conexao.recv(1024)

        if not dados:
            print("[*] Conexão encerrada pelo cliente.")
            break

        expressao = dados.decode("utf-8").strip()

        if expressao.lower() == "sair":
            conexao.sendall(
                "Conexão encerrada pelo servidor.\n".encode("utf-8")
            )
            break

        print(f"[Expressão recebida]: {expressao}")

        try:
            resultado = eval(expressao, {"__builtins__": {}}, {})

            resposta = str(resultado)

        except Exception as e:
            resposta = f"Erro: expressão inválida - {e}"

        conexao.sendall((resposta + "\n").encode("utf-8"))

finally:
    conexao.close()
    server.close()
    print("[*] Servidor finalizado.")