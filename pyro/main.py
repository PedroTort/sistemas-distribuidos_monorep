import Pyro5.server

from pyro_object import Peer

PEER_NAMES = ["PeerA", "PeerB", "PeerC", "PeerD"]
daemon = Pyro5.server.Daemon()
name = input("Nome do Peer (PeerA, PeerB, PeerC, PeerD): ").strip()
uri = daemon.register(Peer(name, PEER_NAMES))
print(uri)
daemon.requestLoop()