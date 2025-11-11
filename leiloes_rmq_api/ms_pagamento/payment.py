import pika
import json
import threading
import time
import random
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from terminal_logger import Logger

RABBITMQ_HOST = "localhost"
EXCHANGE_NAME = "auction"


def get_pika_connection_channel():
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="direct")
    return connection, channel


def notify_rabbit_mq(routing_key: str, body: dict):
    try:
        connection, channel = get_pika_connection_channel()
        channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=routing_key,
            body=json.dumps(body),
        )
        Logger.info(f"MS Pagamento publicou '{routing_key}'")
        connection.close()
    except Exception as e:
        Logger.error(f"MS Pagamento erro ao publicar: {e}")


def handle_auction_winner(body_str: str):
    data = json.loads(body_str)
    auction_name = data.get("auction_name")
    winner_id = data.get("bidder_name")
    valor = data.get("valor_lance")

    Logger.info(
        f"MS Pagamento: Recebido vencedor {winner_id} do leilão {auction_name} (Valor: R$ {valor})"
    )

    if winner_id == "Nenhum lance registrado":
        Logger.info(f"Leilão {auction_name} terminou sem lances.")
        return

    Logger.info(f"Solicitando link de pagamento ao sistema externo para {winner_id}...")
    transacao_id = f"trans_{auction_name}_{winner_id}"
    link_pagamento = f"https://pagamento.mock.com/pay/{transacao_id}"

    Logger.success(f"Link de pagamento gerado: {link_pagamento}")

    link_data = {
        "auction_name": auction_name,
        "bidder_name": winner_id,
        "valor": valor,
        "link_pagamento": link_pagamento,
        "transacao_id": transacao_id,
    }

    notify_rabbit_mq(routing_key="link_pagamento", body=link_data)

    simular_webhook_thread = threading.Thread(
        target=simular_chamada_webhook,
        args=(transacao_id, auction_name, winner_id, valor),
        daemon=True,
    )
    simular_webhook_thread.start()


def simular_chamada_webhook(transacao_id, auction_name, bidder_name, valor):
    time.sleep(10)  # Simula tempo
    status = random.choice(["aprovado", "recusado"])
    Logger.info(f"(MOCK) Sistema externo vai notificar status: {status}")

    webhook_data = {
        "id_transacao": transacao_id,
        "status_pagamento": status,
        "valor": valor,
        "dados_comprador": bidder_name,
        "leilao_id_interno": auction_name,  # Facilitador do Mock
    }

    try:
        requests.post("http://127.0.0.1:5003/webhook/pagamento", json=webhook_data)
    except Exception as e:
        Logger.error(f"(MOCK) Erro ao simular chamada de webhook: {e}")


def start_rmq_consumer():
    Logger.info("Iniciando consumidor RabbitMQ para MS Pagamento...")
    connection, channel = get_pika_connection_channel()

    queue_name = "ms_pagamento_winner_listener"
    routing_key = "leilao_vencedor"

    channel.queue_declare(queue=queue_name, durable=True)
    channel.queue_bind(
        exchange=EXCHANGE_NAME, queue=queue_name, routing_key=routing_key
    )

    def rmq_callback(ch, method, properties, body):
        Logger.info(f"MS Pagamento recebeu evento: {method.routing_key}")
        try:
            handle_auction_winner(body.decode("utf-8"))
        except Exception as e:
            Logger.error(f"Erro ao processar {method.routing_key}: {e}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue=queue_name, on_message_callback=rmq_callback, auto_ack=False
    )

    try:
        channel.start_consuming()
    except Exception as e:
        Logger.error(f"Consumidor RMQ MS-Pagamento parou: {e}")
    finally:
        connection.close()
        Logger.info("Consumidor RabbitMQ do MS Pagamento encerrado.")


# --- API FastAPI ---


class WebhookPayload(BaseModel):
    id_transacao: str
    status_pagamento: str
    valor: float
    dados_comprador: str
    leilao_id_interno: str  # Facilitador do Mock


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicia o consumidor RMQ
    consumer_thread = threading.Thread(target=start_rmq_consumer, daemon=True)
    consumer_thread.start()
    Logger.info("MS Pagamento: Consumidor RabbitMQ iniciado em background.")
    yield
    Logger.info("MS Pagamento: Encerrando.")


app = FastAPI(title="MS Pagamento", lifespan=lifespan)


@app.post("/webhook/pagamento")
def webhook_pagamento(data: WebhookPayload):
    """
    Endpoint que recebe notificações assíncronas do sistema externo.
    """
    Logger.info(f"MS Pagamento: Recebido Webhook! Dados: {data.model_dump_json()}")

    try:
        # Publica 'status_pagamento'
        status_data = {
            "auction_name": data.leilao_id_interno,
            "bidder_name": data.dados_comprador,
            "status_pagamento": data.status_pagamento,
        }
        notify_rabbit_mq(routing_key="status_pagamento", body=status_data)

        Logger.success(
            f"Status '{data.status_pagamento}' publicado para {data.dados_comprador}."
        )
        return {"status": "recebido"}

    except Exception as e:
        Logger.error(f"Erro ao processar webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    Logger.info("MS Pagamento (FastAPI/Webhook) iniciando na porta 5003.")
    uvicorn.run(app, host="0.0.0.0", port=5003)
