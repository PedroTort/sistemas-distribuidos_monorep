from enum import Enum

import pika

class QueueNames(Enum):
    LEILAO_INICIADO = "leilao_iniciado"
    LEILAO_FINALIZADO = "leilao_finalizado"
    LANCE_REALIZADO = "lance_realizado"
    LANCE_VALIDADO = "lance_validado"
    LANCE_VENCEDOR = "leilao_vencedor"
    LEILAO_1 = "leilao_1"
    LEILAO_2 = "leilao_2"

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

def create_queue(channel_intance, queue_name: str, durable: bool=False):
    channel_intance.queue_declare(queue=queue_name, durable=durable)

for queue in QueueNames:
    create_queue(channel, queue.value, True)