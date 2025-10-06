# trab2_peer_pyro5.py

import sys
import threading
import time
import Pyro5.api
import Pyro5.errors
from collections import deque

# --- Constantes de Configuração ---
PEER_NAMES = ["PeerA", "PeerB"]
# PEER_NAMES = ["PeerA", "PeerB", "PeerC", "PeerD"]
HEARTBEAT_INTERVAL = 2
HEARTBEAT_TIMEOUT = 5
REQUEST_TIMEOUT = 5
SC_ACCESS_TIME = 10


# @Pyro5.api.behavior(instance_mode="single")
class Peer:
    def __init__(self, name):
        self.name = name
        self.state = "RELEASED"
        self.request_timestamp = None
        self.proxies = {}
        self.pending_replies = set()
        self.deferred_requests = deque()
        self.last_heartbeat = {
            peer: time.time() for peer in PEER_NAMES if peer != self.name
        }
        self.lock = threading.Lock()
        self.ns = None
        print(f"[{self.name}] Inicializado. Estado: {self.state}")

    def start(self):
        self._connect_to_nameserver()
        self.find_other_peers()
        threading.Thread(target=self._heartbeat_sender, daemon=True).start()
        threading.Thread(target=self._failure_detector, daemon=True).start()
        print(f"[{self.name}] Threads de background iniciadas.")

    def _connect_to_nameserver(self):
        while True:
            try:
                self.ns = Pyro5.api.locate_ns()
                print(f"[{self.name}] Conectado ao Name Server.")
                break
            except Pyro5.errors.NamingError:
                print(
                    f"[{self.name}] Não encontrou o Name Server. Tentando novamente em 3s..."
                )
                time.sleep(3)

    def find_other_peers(self):
        print(f"[{self.name}] Procurando outros peers...")
        for peer_name in PEER_NAMES:
            if peer_name == self.name:
                continue
            while peer_name not in self.proxies.keys():
                try:
                    uri = self.ns.lookup(peer_name)
                    self.proxies[peer_name] = Pyro5.api.Proxy(uri)
                    print(f"[{self.name}] Encontrou {peer_name}!")
                except Pyro5.errors.NamingError:
                    print(
                        f"[{self.name}] ...ainda não encontrou {peer_name}. Tentando em 3s."
                    )
                    time.sleep(3)
        print(f"[{self.name}] Conectado a todos os peers!")

    # --- Operações principais ---
    @Pyro5.api.expose
    def request_access(self, sender_name, timestamp):
        with self.lock:
            should_defer = self.state == "HELD" or (
                self.state == "WANTED" and self.request_timestamp < timestamp
            )
            if should_defer:
                self.deferred_requests.append(sender_name)
            else:
                self.proxies[sender_name].receive_reply(self.name)
        return "OK"

    @Pyro5.api.expose
    def receive_reply(self, sender_name):
        with self.lock:
            if sender_name in self.pending_replies:
                self.pending_replies.remove(sender_name)
            if not self.pending_replies and self.state == "WANTED":
                self._enter_critical_section()
        return "OK"

    @Pyro5.api.expose
    def receive_heartbeat(self, sender_name):
        print(f"[{self.name}] Recebeu heartbeat de {sender_name}.")
        with self.lock:
            if sender_name in self.last_heartbeat:
                self.last_heartbeat[sender_name] = time.time()
        return "OK"

    # --- Seção Crítica ---
    def try_to_enter_sc(self):
        with self.lock:
            if self.state != "RELEASED":
                print(f"[{self.name}] Ação negada. Já está no estado '{self.state}'.")
                return
            print(f"[{self.name}] Quer entrar na Seção Crítica...")
            self.state = "WANTED"
            self.request_timestamp = time.time()
            self.pending_replies = set(self.proxies.keys())
            if not self.pending_replies:
                self._enter_critical_section()
                return

        for name, proxy in list(self.proxies.items()):
            try:
                proxy._pyro_timeout = REQUEST_TIMEOUT
                proxy.request_access(self.name, self.request_timestamp)
            except Exception as e:
                print(f"[{self.name}] FALHA ao enviar pedido para {name}: {e}")
                self._handle_failed_peer(name)

        with self.lock:
            if not self.pending_replies and self.state == "WANTED":
                self._enter_critical_section()

    def _enter_critical_section(self):
        print(
            f"\n>>>>>>>> [{self.name}] Entrou na Seção Crítica! Liberando em {SC_ACCESS_TIME}s. <<<<<<<<\n"
        )
        self.state = "HELD"
        threading.Timer(SC_ACCESS_TIME, self._release_sc).start()

    def _release_sc(self):
        with self.lock:
            if self.state != "HELD":
                return
            print(f"\n<<<<<<<< [{self.name}] Saindo da Seção Crítica. >>>>>>>>\n")
            self.state = "RELEASED"
            while self.deferred_requests:
                peer_name = self.deferred_requests.popleft()
                try:
                    if peer_name in self.proxies:
                        self.proxies[peer_name].receive_reply(self.name)
                except Exception as e:
                    self._handle_failed_peer(peer_name)

    def _heartbeat_sender(self):
        while True:
            time.sleep(HEARTBEAT_INTERVAL)
            for name, proxy in list(self.proxies.items()):
                try:
                    print(f"[{self.name}] Enviando heartbeat para {name}.")
                    proxy.receive_heartbeat(self.name)
                except Exception:
                    pass

    def _failure_detector(self):
        while True:
            time.sleep(HEARTBEAT_TIMEOUT)
            now = time.time()
            for name, last_seen in list(self.last_heartbeat.items()):
                if now - last_seen > HEARTBEAT_TIMEOUT:
                    if name in self.proxies:
                        print(
                            f"\n!!! [{self.name}] TIMEOUT DE HEARTBEAT: {name} considerado FALHO. !!!\n"
                        )
                        self._handle_failed_peer(name)

    def _handle_failed_peer(self, peer_name):
        with self.lock:
            if peer_name in self.proxies:
                del self.proxies[peer_name]
            if peer_name in self.last_heartbeat:
                del self.last_heartbeat[peer_name]
            if peer_name in self.pending_replies:
                self.pending_replies.remove(peer_name)
                if not self.pending_replies and self.state == "WANTED":
                    self._enter_critical_section()
            self.deferred_requests = deque(
                [p for p in self.deferred_requests if p != peer_name]
            )


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in PEER_NAMES:
        print(f"Uso: python {sys.argv[0]} <NomeDoPeer> | Nomes: {PEER_NAMES}")
        return

    peer_name = sys.argv[1]

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
