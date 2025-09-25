import time

import Pyro5.api
import Pyro5.errors
import Pyro5.server

class Peer:
    def __init__(self, name: str):
        self.PEER_NAMES = ["PeerA", "PeerB", "PeerC", "PeerD"]
        self.name = name
        self.proxies = {}
        self.state = "IDLE"
        self.daemon = Pyro5.server.Daemon()
        self.ns = self.setup_name_server()
        self.register_object()
        print(f"[{self.name}] Objeto Peer criado.")


    def register_object(self):
        register_uri = self.daemon.register(self, objectId=f"{self.name}")
        self.ns.register(self.name, register_uri)

    @staticmethod
    def setup_name_server():
        print("Procurando Servidor de Nomes...")
        ns = None
        if not ns:
            try:
                ns = Pyro5.api.locate_ns("localhost", 9090)
                print("Servidor de Nomes encontrado!")
            except Exception as e:
                print("Servidor de Nomes não encontrado.")
                ns = Pyro5.api.start_ns(host="localhost", port=9090)
                print("Servidor de nomes criado")
                time.sleep(5)
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
        for name in self.PEER_NAMES:
            if name == self.name:
                continue
            while name not in self.proxies.keys():
                try:
                    uri = self.ns.lookup(f"{name}")
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

    def request_loop(self):
        self.daemon.requestLoop()
