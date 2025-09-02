from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection

from leiloes_rmq.models.contants import ExchangeNames

class Lance:
    @classmethod
    def __init__(cls, connection: BlockingConnection, channel: BlockingChannel):
        cls.connection = connection
        cls.channel = channel
        cls.exchange_name = ExchangeNames.LEILAO.value
        cls.subscribed_queues = ["lance_realizado","lance_iniciado", "lance_finalizado"]

        cls.channel.exchange_declare(exchange=cls.exchange_name, exchange_type='direct')

    @classmethod
    def callback(cls, ch, method, properties, body):
        try:
            callback_handler = {
                "lance_realizado": cls.handle_bid_made,
                "lance_finalizado": cls.handle_auction_finished
            }
            callback_handler[method.routing_key](method.routing_key, body)

        except Exception as e:
            print(f" [!] Error handling message: {e}")

    @staticmethod
    def handle_bid_made(routing_key: str, body: str):
        print(f" [x] {routing_key}:{body}")

    def handle_auction_finished(self, body):
        pass

    def subscribe_to_queues(self):
        for queue_name in self.subscribed_queues:
            self.channel.queue_declare(queue=queue_name)
            self.channel.queue_bind(
                exchange=self.exchange_name, queue=queue_name, routing_key=queue_name
            )
            self.channel.basic_consume(
                queue=queue_name, on_message_callback=self.callback, auto_ack=True
            )

    def start_listening(self):
        self.subscribe_to_queues()
        print(f"Is now listening to bids at auctions")
        self.channel.start_consuming()
