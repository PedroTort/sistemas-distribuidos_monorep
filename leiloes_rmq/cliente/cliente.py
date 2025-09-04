import json

from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection

class Cliente:
    @classmethod
    def __init__(cls, name: str, connection: BlockingConnection, channel: BlockingChannel):
        cls.name = name
        cls.connection = connection
        cls.channel = channel
        cls.exchange_name = "leilao"
        cls.subscribed_auctions = []

        queue_name = f"leilao_iniciado_{cls.name}"
        cls.channel.queue_declare(queue=queue_name)
        cls.channel.queue_bind(
            exchange=cls.exchange_name, queue=queue_name, routing_key="leilao_iniciado"
        )
        cls.channel.basic_consume(
            queue=queue_name, on_message_callback=cls.callback_leilao_iniciado, auto_ack=True
        )

        cls.channel.exchange_declare(exchange=cls.exchange_name, exchange_type='direct')

    @classmethod
    def callback(cls, ch, method, properties, body):
        print(f" [x] {method.routing_key}:{body}")

    @classmethod
    def callback_leilao_iniciado(cls, ch, method, properties, body):
        body = json.loads(body)
        if body["id_leilao"] in cls.subscribed_auctions:
            print(f" [x] Leilao {body['id_leilao']} inciado!")

    def subscribe_to_auction(self, auction_queue: str):
        if auction_queue not in self.subscribed_auctions:
            self.subscribed_auctions.append(auction_queue)
            queue_name = f"{auction_queue}_{self.name}"
            self.channel.queue_declare(queue=queue_name)
            self.channel.queue_bind(
                exchange=self.exchange_name, queue=queue_name, routing_key=auction_queue
            )
            self.channel.basic_consume(
                queue=queue_name, on_message_callback=self.callback, auto_ack=True
            )

    def bid_to_auction(self, auction_queue: str, bid_value: int):
        if auction_queue in self.subscribed_auctions:
            body = {
                "id_leilao": auction_queue,
                "cliente": self.name,
                "valor_lance": bid_value
            }
            self.channel.basic_publish(
                exchange=self.exchange_name, routing_key="lance_realizado" , body=json.dumps(body)
            )
            print(f" [x] {self.name} bid {bid_value} to {auction_queue}")
        else:
            print(f" [!] {self.name} is not subscribed to {auction_queue}")

    def start_listening(self):
        print(f"{self.name} is now listening to auctions: {self.subscribed_auctions}")
        self.channel.start_consuming()
