import time

import pika

from leiloes_rmq.models.contants import ExchangeNames

connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()
exchange_name = ExchangeNames.LEILAO.value

for i in range(1, 3):
    message="Leilao iniciado"
    auction_name=f"leilao_{i}"
    channel.exchange_declare(exchange=exchange_name, exchange_type="direct")
    channel.basic_publish(
        exchange=exchange_name, routing_key=auction_name, body=message
    )
    print(f" [x] Sent {auction_name}:{message}")
    time.sleep(5)

connection.close()