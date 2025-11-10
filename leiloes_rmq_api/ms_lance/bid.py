import json
import base64
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection
from models import BidModel
from terminal_logger import Logger, TerminalColors, MessageFormatter


class Bid:
    @classmethod
    def __init__(cls, connection: BlockingConnection, channel: BlockingChannel):
        cls.connection = connection
        cls.channel = channel
        cls.exchange_name = "auction"
        cls.subscribed_queues = ["lance_realizado", "leilao_finalizado"]
        cls.channel.exchange_declare(exchange=cls.exchange_name, exchange_type="direct")
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
                "leilao_iniciado": cls.handle_auction_started,
                # "lance_realizado": cls.handle_bid_made,
                "leilao_finalizado": cls.handle_auction_finished,
            }
            callback_handler[method.routing_key](method.routing_key, body)
        except Exception as e:
            Logger.error(
                f"Erro ao processar mensagem da fila {method.routing_key}: {e}"
            )

    @classmethod
    def handle_bid_made(
        cls, active_auctions: list, auction_results: dict, new_bid: BidModel
    ):
        auction_id = new_bid.auction_name
        bid_value = new_bid.bid_value
        current_value = auction_results[auction_id]["current_value"]

        print(f"leilao id: {auction_id}")
        print(f"leiloes ativos: {[auction.name for auction in active_auctions]}")

        if new_bid.auction_name in [auction.name for auction in active_auctions]:
            if bid_value > current_value:
                auction_results[auction_id] = bid_value
                cls.notify_valid_bid(new_bid)
                # message = MessageFormatter.bid_validated(auction_id, client, bid_value)
                # Logger.bid_validated(message)
        else:
            Logger.error(
                f"Lance rejeitado para o leilão {auction_id}: leilão não está ativo."
            )
            return "Lance rejeitado: leilão não está ativo."

        # print(f"Lance recebido - processamento desativado. {new_bid}")
        # body = json.loads(body)
        # try:
        #     body_content = body_with_signature["body"]
        # except Exception as e:
        #     Logger.error(f"Lance inválido ou assinatura incorreta: {e}")
        #     return

        # new_bid = body_with_signature["body"]
        # auction_id = new_bid["id_leilao"]
        # client = new_bid["cliente"]
        # bid_value = new_bid["valor_lance"]

    @classmethod
    def handle_auction_started(cls, routing_key: str, body: str):
        body = json.loads(body)
        auction_id = body.get("auction_id")
        current_value = body.get("current_value")
        cls.auction_results[auction_id] = {
            "id_leilao": auction_id,
            "cliente": "Nenhum lance registrado",
            "valor_lance": current_value,
        }
        Logger.auction_started(f"Leilão {auction_id} iniciado e agora ativo!")

    @classmethod
    def notify_valid_bid(cls, new_bid: BidModel):
        print(f"Notificando lance validado...{new_bid}")
        # cls.channel.basic_publish(
        #     exchange=cls.exchange_name,
        #     routing_key="lance_validado",
        #     body=json.dumps(body),
        # )

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

    def subscribe_to_queue(self, queue_name: str):
        self.channel.queue_declare(queue=queue_name, durable=True)
        self.channel.queue_bind(
            exchange=self.exchange_name, queue=queue_name, routing_key=queue_name
        )
        self.channel.basic_consume(
            queue=queue_name, on_message_callback=self.callback, auto_ack=True
        )
        Logger.info("Inscrição completa em todas as filas de leilão.")

    # def start_listening(self):
    #     self.subscribe_to_queues()
    #     Logger.info("Sistema agora ouvindo todos os lances e eventos de leilão.")
    #     self.channel.start_consuming()
