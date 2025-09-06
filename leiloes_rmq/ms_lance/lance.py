import json
import base64
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from Crypto.Signature import pkcs1_15
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection


class Lance:
    @classmethod
    def __init__(cls, connection: BlockingConnection, channel: BlockingChannel):
        cls.connection = connection
        cls.channel = channel
        cls.exchange_name = "leilao"
        cls.subscribed_queues = ["lance_realizado", "leilao_finalizado", "create_user"]
        cls.active_auctions = []
        cls.auction_results = {}
        cls.channel.exchange_declare(exchange=cls.exchange_name, exchange_type="direct")
        cls.public_keys = {}
        cls.create_auction_start_queue()

    @classmethod
    def create_auction_start_queue(cls):
        queue_name = "leilao_iniciado_lance"
        cls.channel.queue_declare(queue=queue_name, durable=True)
        cls.channel.queue_bind(
            exchange=cls.exchange_name, queue=queue_name, routing_key="leilao_iniciado"
        )
        cls.channel.basic_consume(
            queue=queue_name, on_message_callback=cls.callback, auto_ack=True
        )

    @classmethod
    def callback(cls, ch, method, properties, body):
        try:
            callback_handler = {
                "lance_realizado": cls.handle_bid_made,
                "leilao_iniciado": cls.handle_auction_started,
                "leilao_finalizado": cls.handle_auction_finished,
                "create_user": cls.handle_create_user,
            }
            callback_handler[method.routing_key](method.routing_key, body)

        except Exception as e:
            print(f" [!] Error handling message: {e}")

    @classmethod
    def handle_create_user(cls, routing_key: str, body: str):
        body = json.loads(body)
        user_id = body["user_id"]
        cls.public_keys[user_id] = body["public_key"]

    @classmethod
    def handle_bid_made(cls, routing_key: str, body: str):
        body_with_signature = json.loads(body)

        try:
            signature = body_with_signature["signature"]
            body = body_with_signature["body"]
            cls.validate_signature(signature=signature, body=body)
        except Exception as e:
            return
        new_bid = body_with_signature["body"]
        if new_bid["id_leilao"] in cls.active_auctions:
            current_bid = cls.auction_results[new_bid["id_leilao"]]
            if new_bid["valor_lance"] > current_bid["valor_lance"]:
                cls.auction_results[new_bid["id_leilao"]] = body
                cls.notify_valid_bid(body)

    @classmethod
    def handle_auction_started(cls, routing_key: str, body: str):
        body = json.loads(body)
        cls.active_auctions.append(body.get("id_leilao"))
        cls.auction_results[body.get("id_leilao")] = {
            "id_leilao": body.get("id_leilao"),
            "cliente": "No bids placed",
            "valor_lance": 0,
        }

    @classmethod
    def notify_valid_bid(cls, body: dict):
        print(f"\033[33m Notify Valid Function \n Body: {body}\033[0m")
        cls.channel.basic_publish(
            exchange=cls.exchange_name,
            routing_key="lance_validado",
            body=json.dumps(body),
        )
        print(f" [x] lance_validado:{body}")

    @classmethod
    def handle_auction_finished(cls, routing_key: str, body: str):

        body = json.loads(body)
        queue_name = "leilao_vencedor"

        result = cls.auction_results.get(body.get("id_leilao"))

        cls.channel.basic_publish(
            exchange=cls.exchange_name, routing_key=queue_name, body=json.dumps(result)
        )
        cls.active_auctions.remove(body.get("id_leilao"))

        print(f" [x] Sent {routing_key}:{result}")

    @classmethod
    def validate_signature(cls, signature: str, body: dict) -> None:
        cliente = body["cliente"]
        bytes_signature = base64.b64decode(signature)
        public_key = RSA.import_key(cls.public_keys[cliente])
        hash = SHA256.new(json.dumps(body, sort_keys=True).encode("utf-8"))
        try:
            pkcs1_15.new(public_key).verify(hash, bytes_signature)
            print("The signature is valid.")
        except ValueError as e:
            print("The signature is not valid.")

    def subscribe_to_queues(self):
        for queue_name in self.subscribed_queues:
            self.channel.queue_declare(queue=queue_name, durable=True)
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
