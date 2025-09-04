import json

from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection

class Lance:
    @classmethod
    def __init__(cls, connection: BlockingConnection, channel: BlockingChannel):
        cls.connection = connection
        cls.channel = channel
        cls.exchange_name = "leilao"
        cls.subscribed_queues = ["lance_realizado","leilao_iniciado", "leilao_finalizado"]
        cls.active_auctions = []
        cls.auction_results = {}
        cls.channel.exchange_declare(exchange=cls.exchange_name, exchange_type='direct')

    @classmethod
    def callback(cls, ch, method, properties, body):
        try:
            callback_handler = {
                "lance_realizado": cls.handle_bid_made,
                "leilao_iniciado": cls.handle_auction_started,
                "leilao_finalizado": cls.handle_auction_finished
            }
            callback_handler[method.routing_key](method.routing_key, body)

        except Exception as e:
            print(f" [!] Error handling message: {e}")

    @classmethod
    def handle_bid_made(cls, routing_key: str, body: str):
        new_bid = json.loads(body)
        if new_bid["id_leilao"] in cls.active_auctions:
            current_bid = cls.auction_results[routing_key]
            if new_bid["valor_lance"] > current_bid["valor_lance"]:
                cls.auction_results[routing_key] = body
                cls.notify_valid_bid(body)

    @classmethod
    def handle_auction_started(cls, routing_key: str, body: str):
        body = json.loads(body)
        cls.active_auctions.append(body.get("id_leilao"))
        cls.auction_results[body.get("id_leilao")] = {
            "id_leilao": body.get("id_leilao"),
            "cliente": "No bids placed",
            "valor_lance": 0
        }

    @classmethod
    def notify_valid_bid(cls, body: str):
        exchange_name = "leilao"
        cls.channel.exchange_declare(exchange=exchange_name, exchange_type="direct")
        cls.channel.basic_publish(
            exchange=exchange_name, routing_key="lance_validado", body=json.dumps(body)
        )
        print(f" [x] lance_validado:{body}")

    @classmethod
    def handle_auction_finished(cls, routing_key: str, body: str):
        body = json.loads(body)
        queue_name = "leilao_vencedor"

        result = cls.auction_results.get(body.get("id_leilao"))

        exchange_name = "leilao"
        cls.channel.exchange_declare(exchange=exchange_name, exchange_type="direct")
        cls.channel.basic_publish(
            exchange=exchange_name, routing_key=queue_name, body=json.dumps(result)
        )
        print(f" [x] Sent {routing_key}:{result}")

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
