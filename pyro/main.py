from pyro_object import Peer

name = input("Nome do Peer (PeerA, PeerB, PeerC, PeerD): ").strip()
peer = Peer(name)
peer.request_loop()
