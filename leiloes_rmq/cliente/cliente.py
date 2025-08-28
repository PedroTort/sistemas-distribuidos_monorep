import pika
from leiloes_rmq.models.contants import QueueNames

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

queue_name = QueueNames.LEILAO_INICIADO.value
exchange_name = QueueNames.LEILAO.value
severities = ["info"]
channel.exchange_declare(exchange=exchange_name, exchange_type='direct')

def callback(ch, method, properties, body):
    channel.queue_bind(
        exchange=exchange_name, queue=body.decode(), routing_key=severities[0]
    )
    print(f" [x] {method.routing_key}:{body}")


channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()
