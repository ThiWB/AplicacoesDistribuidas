import sys
import socket

HOST = '127.0.0.1'
PORT = 5000

if len(sys.argv) > 1:
    HOST = sys.argv[1]

if len(sys.argv) > 2:
    try:
        PORT = int(sys.argv[2])
    except ValueError:
        print("Erro: a porta deve ser um número inteiro.")
        sys.exit(1)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    print(f"[*] Conectando a {HOST}:{PORT}...")
    client.connect((HOST, PORT))

    print("[+] Conectado!")
    print("Digite uma expressão matemática.")
    print("Exemplo: 40+2")
    print("Digite 'sair' para encerrar.")
    print("-" * 50)

    while True:
        expressao = input("Expressão > ").strip()

        if not expressao:
            continue

        client.sendall(expressao.encode("utf-8"))

        if expressao.lower() == "sair":
            break

        resposta = client.recv(1024)

        if not resposta:
            print("[*] Servidor encerrou a conexão.")
            break

        print("Resultado <", resposta.decode("utf-8").strip())

finally:
    client.close()
    print("[*] Cliente finalizado.")