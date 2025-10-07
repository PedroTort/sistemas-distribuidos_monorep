import sys
import threading
import Pyro5.api
import Pyro5.errors

from peer import Peer, PEER_NAMES

def main():
    if len(sys.argv) < 2 or sys.argv[1] not in PEER_NAMES:
        print(f"Uso: python {sys.argv[0]} <NomeDoPeer> | Nomes: {PEER_NAMES}")
        return

    peer_name = sys.argv[1]
    Pyro5.config.SERVERTYPE = "thread"
    daemon = Pyro5.api.Daemon()
    ns = Pyro5.api.locate_ns()
    peer = Peer(peer_name)
    uri = daemon.register(peer)
    ns.register(peer_name, uri)
    print(f"[{peer_name}] Registrado no PyRO. URI: {uri}")
    peer.start()

    def user_interface():
        while True:
            try:
                cmd = (
                    input("Digite 'req' para solicitar a SC ou 'exit' para sair:\n> ")
                    .strip()
                    .lower()
                )
                if cmd == "req":
                    peer.try_to_enter_sc()
                elif cmd == "exit":
                    break
            except (EOFError, KeyboardInterrupt):
                break

    threading.Thread(target=user_interface, daemon=True).start()
    print(f"[{peer_name}] Pronto para receber chamadas e comandos.")

    try:
        daemon.requestLoop()
    finally:
        print(f"[{peer_name}] Encerrando e removendo registro do Name Server.")
        ns.remove(peer_name)


if __name__ == "__main__":
    main()
