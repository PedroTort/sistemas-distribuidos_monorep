import pika
import time
import json
from datetime import datetime, timedelta

from models import AuctionModel
from ms_leilao.auction_lifecycle import AuctionLifecycle
from terminal_logger import Logger


class Auction:
    def __init__(
        self,
        auction_model: AuctionModel,
    ):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters("localhost")
        )
        self.channel = self.connection.channel()
        self.auction_model = auction_model
        self.exchange_name = "auction"
        self.channel.exchange_declare(
            exchange=self.exchange_name, exchange_type="direct"
        )

    def run_auction(self):
        try:
            lifecycle_thread = AuctionLifecycle(auction_model=self.auction_model)
            lifecycle_thread.start()

            Logger.success(f"Leilão {self.auction_model.auction_id} criado e agendado.")
            return {"message": "ok", "status_code": 200}
        except Exception as e:
            Logger.error(f"Erro ao criar leilão: {e}")
            return {"erro": str(e)}
