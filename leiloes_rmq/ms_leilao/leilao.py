import time

import pika

from leiloes_rmq.models.contants import QueueNames

connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()
exchange_name = QueueNames.LEILAO.value

for i in range(1, 3):
    message=f"leilao_{i}"
    severity="info"
    channel.exchange_declare(exchange=exchange_name, exchange_type="direct")
    channel.basic_publish(
        exchange=exchange_name, routing_key=severity, body=message
    )
    print(f" [x] Sent {severity}:{message}")
    time.sleep(5)

connection.close()