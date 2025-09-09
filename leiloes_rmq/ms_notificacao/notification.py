import json
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection
from terminal_logger import Logger, TerminalColors


class Notification:
    @classmethod
    def __init__(cls, connection: BlockingConnection, channel: BlockingChannel):
        cls.connection = connection
        cls.channel = channel
        cls.exchange_name = "auction"
        cls.channel.exchange_declare(exchange=cls.exchange_name, exchange_type="direct")

        for queue_name in ["lance_validado", "leilao_vencedor"]:
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
                "leilao_vencedor": cls.handle_auction_winner,
            }
            callback_handler[method.routing_key](body)
        except Exception as e:
            Logger.error(
                f"Erro ao processar mensagem da fila {method.routing_key}: {e}"
            )

    @classmethod
    def handle_bid_validated(cls, body: str):
        data = json.loads(body)
        auction_id = data["id_leilao"]
        client = data["cliente"]
        bid_value = data["valor_lance"]
        cls.channel.exchange_declare(exchange=cls.exchange_name, exchange_type="direct")
        cls.channel.basic_publish(
            exchange=cls.exchange_name, routing_key=auction_id, body=body
        )
        Logger.bid_validated(
            f"Lance validado enviado para o leilão {TerminalColors.BOLD}{auction_id}{TerminalColors.RESET}\n"
            f"  Cliente: {TerminalColors.CYAN}{client}{TerminalColors.RESET}\n"
            f"  Valor do lance: {TerminalColors.GREEN}{bid_value}{TerminalColors.RESET}"
        )

    @classmethod
    def handle_auction_winner(cls, body: str):
        data = json.loads(body)
        auction_id = data["id_leilao"]
        client = data["cliente"]
        bid_value = data["valor_lance"]
        data["auction_winner_flag"] = True

        cls.channel.exchange_declare(exchange=cls.exchange_name, exchange_type="direct")
        cls.channel.basic_publish(
            exchange=cls.exchange_name, routing_key=auction_id, body=json.dumps(data)
        )

        Logger.auction_winner(
            f"Resultado do leilão {TerminalColors.BOLD}{auction_id}{TerminalColors.RESET} enviado:\n"
            f"  Vencedor: {TerminalColors.CYAN}{client}{TerminalColors.RESET}\n"
            f"  Valor do lance: {TerminalColors.GREEN}{bid_value}{TerminalColors.RESET}"
        )

    def start_listening(self):
        Logger.info("Sistema de notificações inicializado e ouvindo filas de eventos.")
        self.channel.start_consuming()
