import json
import base64
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection

class Cliente:
    def __init__(self, name: str, connection: BlockingConnection, channel: BlockingChannel, private_key_bytes: bytes=None, public_key_bytes: dict=None):
        self.name = name
        self.private_key_bytes = private_key_bytes
        self.connection = connection
        self.channel = channel
        self.exchange_name = "leilao"
        self.subscribed_auctions = []
        queue_name = f"leilao_iniciado_{self.name}"
        self.channel.exchange_declare(exchange=self.exchange_name, exchange_type='direct')
        self.channel.queue_declare(queue=queue_name, durable=True)
        self.channel.queue_bind(
            exchange=self.exchange_name, queue=queue_name, routing_key="leilao_iniciado"
        )
        self.channel.basic_consume(
            queue=queue_name, on_message_callback=self.callback_leilao_iniciado, auto_ack=True
        )
        if public_key_bytes is not None:
            public_key_dict = {
                "user_id": self.name,
                "public_key": public_key_bytes.decode('utf-8'),
            }
            self.channel.basic_publish(
                exchange=self.exchange_name, routing_key="create_user", body=json.dumps(public_key_dict, sort_keys=True)
            )


    def callback(self, ch, method, properties, body):
        print(f" [x] {method.routing_key}:{body}")

    def callback_leilao_iniciado(self, ch, method, properties, body):
        body = json.loads(body)
        if body["id_leilao"] in self.subscribed_auctions:
            print(f" [x] Leilao {body['id_leilao']} inciado!")

    def subscribe_to_auction(self, auction_queue: str):
        if auction_queue not in self.subscribed_auctions:
            self.subscribed_auctions.append(auction_queue)
            queue_name = f"{auction_queue}_{self.name}"
            self.channel.queue_declare(queue=queue_name, durable=True)
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
            private_key = RSA.import_key(self.private_key_bytes)
            hash = SHA256.new(json.dumps(body, sort_keys=True).encode('utf-8'))
            signature = pkcs1_15.new(private_key).sign(hash)
            body_with_signature = {
                "body": body,
                "signature": base64.b64encode(signature).decode("utf-8")
            }
            self.channel.basic_publish(
                exchange=self.exchange_name, routing_key="lance_realizado" , body=json.dumps(body_with_signature)
            )
            print(f" [x] {self.name} bid {bid_value} to {auction_queue}")
        else:
            print(f" [!] {self.name} is not subscribed to {auction_queue}")

    def start_listening(self):
        print(f"{self.name} is now listening to auctions: {self.subscribed_auctions}")
        self.channel.start_consuming()
