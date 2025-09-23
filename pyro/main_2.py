import Pyro5.server

from pyro_object import Peer

PEER_NAMES = ["PeerA", "PeerB", "PeerC", "PeerD"]
daemon = Pyro5.server.Daemon()
name = input("Nome do Peer (PeerA, PeerB, PeerC, PeerD): ").strip()
peer = Peer(name, PEER_NAMES)
uri = daemon.register(peer)
print(uri)
peer.find_other_peers()
peer.start_ping_test()