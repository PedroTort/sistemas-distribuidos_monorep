import pika

from leiloes_rmq.ms_notificacao.notification import Notification

connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()

lance = Notification(connection, channel)
lance.start_listening()

connection.close()
