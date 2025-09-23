import time

import Pyro5.api
import Pyro5.errors
import Pyro5.server

class Peer:
    def __init__(self, name: str, peer_names: list[str]):
        self.name = name
        self.proxies = {}
        self.state = "IDLE"
        self.peer_names = peer_names
        self.ns = self.setup_name_server()
        print(f"[{self.name}] Objeto Peer criado.")

    @staticmethod
    def setup_name_server():
        print("Procurando Servidor de Nomes...")
        ns = None
        if not ns:
            try:
                ns = Pyro5.api.locate_ns("localhost", 9090)
                print("Servidor de Nomes encontrado!")
            except Exception:
                print("Servidor de Nomes não encontrado.")
                ns = Pyro5.api.start_ns(host="localhost")
                print("Servidor de nomes criado")
                time.sleep(5)
        print("bb")
        return ns

    @Pyro5.api.expose
    def ping(self, sender_name: str):
        print(f"[{self.name}] Recebeu um PING de [{sender_name}]")
        return f"PONG de {self.name}"

    @Pyro5.api.expose
    def request_access(self, remote_timestamp: int, remote_peer_name: str):
        print(f"[{self.name}] Recebeu pedido de {remote_peer_name} com timestamp {remote_timestamp}")
        return "OK"

    def find_other_peers(self):
        print(f"[{self.name}] Procurando outros peers...")
        for name in self.peer_names:
            if name == self.name:
                continue
            while name not in self.proxies:
                try:

                    uri = self.ns.lookup(name)
                    self.proxies[name] = Pyro5.api.Proxy(uri)
                    print(f"[{self.name}] Encontrou {name}!")
                except Pyro5.errors.NamingError:
                    print(f"[{self.name}] ...ainda não encontrou {name}. Tentando em 3s.")
                    time.sleep(3)
        print(f"[{self.name}] Conectado a todos os peers!")

    def start_ping_test(self):
        print(f"\n[{self.name}] === INICIANDO TESTE DE PING ===")
        for name, proxy in self.proxies.items():
            try:
                response = proxy.ping(self.name)
                print(f"[{self.name}] Resposta de {name}: {response}")
            except Exception as e:
                print(f"[{self.name}] Erro ao pingar {name}: {e}")
        print(f"[{self.name}] === FIM DO TESTE DE PING ===\n")