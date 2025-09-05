import json
import time
from datetime import datetime, timedelta

import pika

connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()
exchange_name = "leilao"
channel.exchange_declare(exchange=exchange_name, exchange_type="direct")

for i in range(1, 3):
    body={
        "id_leilao": f"leilao_{i}",
        "start_time": datetime.now().strftime("%H:%M:%S"),
        "end_time": (datetime.now() + timedelta(seconds=5)).strftime("%H:%M:%S")

    }
    queue_name="leilao_iniciado"
    channel.basic_publish(
        exchange=exchange_name, routing_key=queue_name, body=json.dumps(body)
    )
    print(f" [x] Sent {queue_name}:{body}")
    time.sleep(5)

for i in range(1, 3):
    body={
        "id_leilao": f"leilao_{i}"
    }
    queue_name="leilao_finalizado"
    channel.basic_publish(
        exchange=exchange_name, routing_key=queue_name, body=json.dumps(body)
    )
    print(f" [x] Sent {queue_name}:{body}")
    time.sleep(5)

connection.close()