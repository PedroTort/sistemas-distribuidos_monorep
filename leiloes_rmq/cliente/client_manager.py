import pika

from leiloes_rmq.cliente.cliente import Cliente
from leiloes_rmq.models.contants import QueueNames

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost')
)
channel = connection.channel()

cliente_1 = Cliente("Ana", connection, channel)
# cliente_2 = Cliente("Bruno",connection, channel)

cliente_1.subscribe_to_auction(QueueNames.LEILAO_1.value)
# cliente_2.subscribe_to_auction(QueueNames.LEILAO_1.value)
# cliente_2.subscribe_to_auction(QueueNames.LEILAO_2.value)

cliente_1.start_listening()
# cliente_2.start_listening()
