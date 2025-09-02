import pika

from leiloes_rmq.models.contants import ExchangeNames
from leiloes_rmq.ms_lance.lance import Lance

connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()
exchange_name = ExchangeNames.LEILAO.value

lance = Lance(connection, channel)
lance.start_listening()

connection.close()
