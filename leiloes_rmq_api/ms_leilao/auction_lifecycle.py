import pika
import time
import json
from threading import Thread
from datetime import datetime, timezone, timedelta

from models import AuctionModel
from terminal_logger import Logger

RABBITMQ_HOST = "localhost"
EXCHANGE_NAME = "auction"


class AuctionLifecycle(Thread):
    def __init__(self, auction_model: AuctionModel):
        super().__init__()
        self.auction_model = auction_model

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(RABBITMQ_HOST)
        )
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="direct")

    def run(self):
        wait_seconds = (
            self.auction_model.start_date - datetime.now(timezone(timedelta(hours=-3)))
        ).total_seconds()
        if wait_seconds > 0:
            Logger.info(
                f"Leilão {self.auction_model.name} esperando {wait_seconds:.0f}s para iniciar."
            )
            time.sleep(wait_seconds)

        self.channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key="leilao_iniciado",
            body=json.dumps(self.auction_model.to_dict()),
        )

        Logger.auction_started(
            f"{self.auction_model.name} ('{self.auction_model.description}') iniciado."
        )

        duration = (
            self.auction_model.end_date - self.auction_model.start_date
        ).total_seconds()
        if duration > 0:
            time.sleep(duration)

        self.channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key="leilao_finalizado",
            body=json.dumps(self.auction_model.to_dict()),
        )

        Logger.auction_ended(f"{self.auction_model.name} finalizado")

        self.connection.close()
