import pika
import time
import json
from datetime import datetime, timedelta
from leiloes_rmq.terminal_logger import Logger


class Auction:
    def __init__(
        self,
        auction_id: str,
        duration: int,
    ):
        self.auction_id = auction_id
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters("localhost")
        )
        self.duration = duration
        self.channel = self.connection.channel()
        self.exchange_name = "auction"
        self.channel.exchange_declare(
            exchange=self.exchange_name, exchange_type="direct"
        )

    def start_auction(self):
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=self.duration)

        body = {
            "id_leilao": self.auction_id,
            "start_time": start_time.strftime("%H:%M:%S"),
            "end_time": end_time.strftime("%H:%M:%S"),
        }
        self.channel.basic_publish(
            exchange=self.exchange_name,
            routing_key="leilao_iniciado",
            body=json.dumps(body),
        )
        Logger.auction_started(
            f"{self.auction_id} iniciado às {body['start_time']} (duração: {self.duration}s)"
        )

        time.sleep(self.duration)

        body = {
            "id_leilao": self.auction_id,
            "end_time": datetime.now().strftime("%H:%M:%S"),
        }
        self.channel.basic_publish(
            exchange=self.exchange_name,
            routing_key="leilao_finalizado",
            body=json.dumps(body),
        )
        Logger.auction_ended(f"{self.auction_id} finalizado às {body['end_time']}")
