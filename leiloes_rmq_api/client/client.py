import json
import pika
import base64
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from terminal_logger import Logger, MessageFormatter


class Client:
    def __init__(
        self,
        name: str,
        type: str,
        private_key_bytes: bytes = None,
        public_key_bytes: dict = None,
    ):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters("localhost")
        )
        self.channel = self.connection.channel()
        self.name = name
        self.private_key_bytes = private_key_bytes
        self.exchange_name = "auction"
        self.subscribed_auctions = []
        self.type = type

        if type == "bidder":
            public_key_dict = {
                "user_id": self.name,
                "public_key": public_key_bytes.decode("utf-8"),
            }
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key="create_user",
                body=json.dumps(public_key_dict, sort_keys=True),
            )
            Logger.info(f"Cliente {self.name} cadastrado como licitante no sistema.")

        if type == "listener":
            self.subscribe_to_auction_start()
            Logger.info(f"Cliente {self.name} cadastrado como ouvinte de leilões.")

    def callback(self, ch, method, properties, body):
        body_str = body.decode("utf-8")
        body_json = json.loads(body_str)
        auction_id = body_json.get("id_leilao")
        client = body_json.get("cliente")
        bid_value = body_json.get("valor_lance")

        if body_json.get("auction_winner_flag"):
            message = MessageFormatter.auction_winner(auction_id, client, bid_value)
            Logger.auction_winner(message)
        else:
            message = MessageFormatter.new_bid_notification(
                method.routing_key, auction_id, client, bid_value
            )
            Logger.info(message)

    def callback_auction_started(self, ch, method, properties, body):
        data = json.loads(body)
        auction_id = data["id_leilao"]

        if auction_id in self.subscribed_auctions:
            description = data["description"]
            start_time = data["start_time"]
            end_time = data["end_time"]

            message = MessageFormatter.auction_started(
                auction_id, description, start_time, end_time
            )
            Logger.auction_started(message)

    def subscribe_to_auction(self, auction_queue: str):
        if auction_queue not in self.subscribed_auctions:
            self.subscribed_auctions.append(auction_queue)

            if self.type == "listener":
                queue_name = f"{auction_queue}_{self.name}"
                self.channel.queue_declare(queue=queue_name, durable=True)
                self.channel.queue_bind(
                    exchange=self.exchange_name,
                    queue=queue_name,
                    routing_key=auction_queue,
                )
                self.channel.basic_consume(
                    queue=queue_name, on_message_callback=self.callback, auto_ack=True
                )
                Logger.info(f"Ouvinte {self.name} inscrito no leilão {auction_queue}.")

    def bid_to_auction(self, auction_queue: str, bid_value: int):
        if auction_queue in self.subscribed_auctions:
            body = {
                "id_leilao": auction_queue,
                "cliente": self.name,
                "valor_lance": bid_value,
            }
            private_key = RSA.import_key(self.private_key_bytes)
            hash = SHA256.new(json.dumps(body, sort_keys=True).encode("utf-8"))
            signature = pkcs1_15.new(private_key).sign(hash)
            body_with_signature = {
                "body": body,
                "signature": base64.b64encode(signature).decode("utf-8"),
            }
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key="lance_realizado",
                body=json.dumps(body_with_signature),
            )
            Logger.bid_placed(
                f"Cliente {self.name} | Leilão: {auction_queue} | Valor do lance: {bid_value}"
            )
        else:
            Logger.error(
                f"Cliente {self.name} não está inscrito no leilão {auction_queue}"
            )

    def start_listening(self):
        Logger.info(
            f"{self.name} agora está ouvindo leilões: {self.subscribed_auctions}"
        )
        self.channel.start_consuming()

    def subscribe_to_auction_start(self):
        queue_name = f"leilao_iniciado_{self.name}"
        self.channel.exchange_declare(
            exchange=self.exchange_name, exchange_type="direct"
        )
        self.channel.queue_declare(queue=queue_name, durable=True)
        self.channel.queue_bind(
            exchange=self.exchange_name, queue=queue_name, routing_key="leilao_iniciado"
        )
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=self.callback_auction_started,
            auto_ack=True,
        )
        Logger.info(
            f"Cliente {self.name} inscrito para receber notificações de leilões iniciados."
        )
