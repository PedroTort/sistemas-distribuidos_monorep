import pika
import time
import json
from datetime import datetime, timezone, timedelta
from threading import Thread
from terminal_logger import Logger

RABBITMQ_HOST = "localhost"
EXCHANGE_NAME = "auction"


class AuctionLifecycle(Thread):
    def __init__(self, auction_name: str, description: str, start_date: datetime, end_date: datetime,
                 current_value: float):
        super().__init__()
        self.auction_name = auction_name
        self.description = description
        self.start_date = start_date
        self.end_date = end_date
        self.current_value = current_value
        self.status = "nao_iniciado"

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="direct")

    def run(self):
        wait_seconds = (self.start_date - datetime.now(timezone(timedelta(hours=-3)))).total_seconds()
        if wait_seconds > 0:
            Logger.info(f"Leilão {self.auction_name} esperando {wait_seconds:.0f}s para iniciar.")
            time.sleep(wait_seconds)

        self.status = "ativo"
        start_date_str = self.start_date.strftime("%Y-%m-%d %H:%M:%S")
        end_date_str = self.end_date.strftime("%Y-%m-%d %H:%M:%S")

        body = {
            "auction_name": self.auction_name,
            "description": self.description,
            "start_date": start_date_str,
            "end_date": end_date_str,
            "current_value": self.current_value
        }
        self.channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key="leilao_iniciado",
            body=json.dumps(body),
        )
        Logger.auction_started(
            f"{self.auction_name} ('{self.description}') iniciado às {start_date_str}."
        )

        duration = (self.end_date - self.start_date).total_seconds()
        if duration > 0:
            time.sleep(duration)

        self.status = "encerrado"
        body_final = {
            "auction_name": self.auction_name,
            "end_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key="leilao_finalizado",
            body=json.dumps(body_final),
        )
        Logger.auction_ended(
            f"{self.auction_name} finalizado às {body_final['end_date']}"
        )

        self.connection.close()
