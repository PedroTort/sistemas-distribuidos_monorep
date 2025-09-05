import json

from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection

class Notification:
    @classmethod
    def __init__(cls, connection: BlockingConnection, channel: BlockingChannel):
        cls.connection = connection
        cls.channel = channel
        cls.exchange_name = "leilao"
        cls.channel.exchange_declare(exchange=cls.exchange_name, exchange_type='direct')
        for queue_name in ["lance_validado","leilao_vencedor"]:
            cls.channel.queue_declare(queue=queue_name, durable=True)
            cls.channel.queue_bind(
                exchange=cls.exchange_name, queue=queue_name, routing_key=queue_name
            )
            cls.channel.basic_consume(
                queue=queue_name, on_message_callback=cls.callback, auto_ack=True
            )

    @classmethod
    def callback(cls, ch, method, properties, body):
        try:
            callback_handler = {
                "lance_validado": cls.handle_bid_validated,
                "leilao_vencedor": cls.handle_auction_winner
            }
            callback_handler[method.routing_key](body)

        except Exception as e:
            print(f" [!] Error handling message: {e}")

    @classmethod
    def handle_bid_validated(cls, body: str):
        id_leilao = json.loads(body)["id_leilao"]
        cls.channel.exchange_declare(exchange=cls.exchange_name, exchange_type="direct")
        cls.channel.basic_publish(
            exchange=cls.exchange_name, routing_key=id_leilao, body=body
        )
        print(f" [x] lance_validado:{body}")

    @classmethod
    def handle_auction_winner(cls, body: str):
        id_leilao = json.loads(body)["id_leilao"]
        cls.channel.exchange_declare(exchange=cls.exchange_name, exchange_type="direct")
        cls.channel.basic_publish(
            exchange=cls.exchange_name, routing_key=id_leilao, body=body
        )
        print(f" [x] leilao_vencedor:{body}")

    def start_listening(self):
        print(f"Is now listening to notifications")
        self.channel.start_consuming()
