import pika

from leiloes_rmq.cliente.cliente import Cliente

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost')
)
channel = connection.channel()

# cliente_1 = Cliente("Ana", connection, channel)
cliente_2 = Cliente("Bruno",connection, channel)

# cliente_1.subscribe_to_auction("leilao_1")
cliente_2.subscribe_to_auction("leilao_1")
cliente_2.subscribe_to_auction("leilao_2")

cliente_2.bid_to_auction("leilao_2", 150)

# cliente_1.start_listening()
cliente_2.start_listening()
