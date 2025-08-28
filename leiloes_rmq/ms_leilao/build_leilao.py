from leiloes_rmq.models.contants import QueueNames
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

def create_queue(channel_intance, queue_name: str, durable: bool):
    channel_intance.queue_declare(queue=queue_name, durable=durable)

for queue in QueueNames:
    create_queue(channel, queue.value, True)