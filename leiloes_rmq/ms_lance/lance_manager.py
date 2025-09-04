import pika
from leiloes_rmq.ms_lance.lance import Lance

connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()
exchange_name = "leilao"

lance = Lance(connection, channel)
lance.start_listening()

connection.close()
