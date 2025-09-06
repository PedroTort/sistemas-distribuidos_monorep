import pika
from leiloes_rmq.ms_lance.bid import Bid

connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()

lance = Bid(connection, channel)
lance.start_listening()

connection.close()
