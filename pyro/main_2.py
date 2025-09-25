import Pyro5.server

from pyro_object import Peer

name = input("Nome do Peer (PeerA, PeerB, PeerC, PeerD): ").strip()
peer = Peer(name)
peer.find_other_peers()
peer.start_ping_test()
