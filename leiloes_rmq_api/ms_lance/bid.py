import json
import base64
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection
from terminal_logger import Logger, TerminalColors, MessageFormatter


class Bid:
    @classmethod
    def __init__(cls, connection: BlockingConnection, channel: BlockingChannel):
        cls.connection = connection
        cls.channel = channel
        cls.exchange_name = "auction"
        cls.subscribed_queues = ["lance_realizado", "leilao_finalizado", "create_user"]
        cls.active_auctions = []
        cls.auction_results = {}
        cls.channel.exchange_declare(exchange=cls.exchange_name, exchange_type="direct")
        cls.public_keys = {}
        cls.create_auction_start_queue()
        Logger.info("Sistema de lances inicializado e pronto para receber eventos.")

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
        Logger.info("Inscrito para receber notificações de leilões iniciados.")

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
            Logger.error(
                f"Erro ao processar mensagem da fila {method.routing_key}: {e}"
            )

    @classmethod
    def handle_create_user(cls, routing_key: str, body: str):
        body = json.loads(body)
        user_id = body["user_id"]
        cls.public_keys[user_id] = body["public_key"]
        Logger.info(f"Usuário cadastrado no sistema: {user_id}")

    @classmethod
    def handle_bid_made(cls, routing_key: str, body: str):
        body_with_signature = json.loads(body)
        try:
            signature = body_with_signature["signature"]
            body_content = body_with_signature["body"]
            cls.validate_signature(signature=signature, body=body_content)
        except Exception as e:
            Logger.error(f"Lance inválido ou assinatura incorreta: {e}")
            return

        new_bid = body_with_signature["body"]
        auction_id = new_bid["id_leilao"]
        client = new_bid["cliente"]
        bid_value = new_bid["valor_lance"]

        if auction_id in cls.active_auctions:
            current_bid = cls.auction_results[auction_id]
            if bid_value > current_bid["valor_lance"]:
                cls.auction_results[auction_id] = new_bid
                cls.notify_valid_bid(new_bid)
                message = MessageFormatter.bid_validated(auction_id, client, bid_value)
                Logger.bid_validated(message)

    @classmethod
    def handle_auction_started(cls, routing_key: str, body: str):
        body = json.loads(body)
        auction_id = body.get("id_leilao")
        cls.active_auctions.append(auction_id)
        cls.auction_results[auction_id] = {
            "id_leilao": auction_id,
            "cliente": "Nenhum lance registrado",
            "valor_lance": 0,
        }
        Logger.auction_started(f"Leilão {auction_id} iniciado e agora ativo!")

    @classmethod
    def notify_valid_bid(cls, body: dict):
        cls.channel.basic_publish(
            exchange=cls.exchange_name,
            routing_key="lance_validado",
            body=json.dumps(body),
        )

    @classmethod
    def handle_auction_finished(cls, routing_key: str, body: str):
        body = json.loads(body)
        auction_id = body.get("id_leilao")
        winner = cls.auction_results.get(auction_id)
        winner_name = winner["cliente"]
        bid_value = winner["valor_lance"]

        cls.channel.basic_publish(
            exchange=cls.exchange_name,
            routing_key="leilao_vencedor",
            body=json.dumps(winner),
        )
        if auction_id in cls.active_auctions:
            cls.active_auctions.remove(auction_id)

        message = MessageFormatter.auction_ended(auction_id, winner_name, bid_value)
        Logger.auction_ended(message)

    @classmethod
    def validate_signature(cls, signature: str, body: dict) -> None:
        cliente = body["cliente"]
        bytes_signature = base64.b64decode(signature)
        public_key = RSA.import_key(cls.public_keys[cliente])
        hash = SHA256.new(json.dumps(body, sort_keys=True).encode("utf-8"))
        try:
            pkcs1_15.new(public_key).verify(hash, bytes_signature)
            Logger.info(
                f"Assinatura válida do cliente {cliente} para o lance no leilão {body['id_leilao']}."
            )
        except ValueError:
            Logger.error(
                f"Assinatura inválida do cliente {cliente} para o lance no leilão {body['id_leilao']}."
            )

    def subscribe_to_queues(self):
        for queue_name in self.subscribed_queues:
            self.channel.queue_declare(queue=queue_name, durable=True)
            self.channel.queue_bind(
                exchange=self.exchange_name, queue=queue_name, routing_key=queue_name
            )
            self.channel.basic_consume(
                queue=queue_name, on_message_callback=self.callback, auto_ack=True
            )
        Logger.info("Inscrição completa em todas as filas de leilão.")

    def start_listening(self):
        self.subscribe_to_queues()
        Logger.info("Sistema agora ouvindo todos os lances e eventos de leilão.")
        self.channel.start_consuming()
