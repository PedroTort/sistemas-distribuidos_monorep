import pika
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection

from leiloes_rmq.models.contants import QueueNames, ExchangeNames


class Cliente:
    @classmethod
    def __init__(cls, name: str, connection: BlockingConnection, channel: BlockingChannel):
        cls.name = name
        cls.connection = connection
        cls.channel = channel
        cls.exchange_name = ExchangeNames.LEILAO.value
        cls.subscribed_auctions = []

        cls.channel.exchange_declare(exchange=cls.exchange_name, exchange_type='direct')

    @classmethod
    def callback(cls, ch, method, properties, body):
        print(f" [x] {method.routing_key}:{body}")

    def subscribe_to_auction(self, auction_queue: str):
        if auction_queue not in self.subscribed_auctions:
            self.subscribed_auctions.append(auction_queue)
            queue_name = auction_queue  # Each auction has its own queue
            self.channel.queue_declare(queue=queue_name)
            self.channel.queue_bind(
                exchange=self.exchange_name, queue=queue_name, routing_key=queue_name
            )
            self.channel.basic_consume(
                queue=queue_name, on_message_callback=self.callback, auto_ack=True
            )
            print(f"{self.name} subscribed to auction: {auction_queue}")

    def start_listening(self):
        print(f"{self.name} is now listening to auctions: {self.subscribed_auctions}")
        self.channel.start_consuming()
