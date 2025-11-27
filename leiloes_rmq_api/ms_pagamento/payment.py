import pika
import json
import threading
import random
import requests
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from contextlib import asynccontextmanager
from terminal_logger import Logger

RABBITMQ_HOST = "localhost"
EXCHANGE_NAME = "auction"
EXTERNAL_BANK_URL = "http://localhost:5004/api/payments"
MY_WEBHOOK_URL = "http://localhost:5003/webhook/pagamento"

payment_store: dict[str, dict] = {}

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

def request_payment_link_external(auction_name, winner_name, amount):
    payload = {
        "amount": amount,
        "client_name": winner_name,
        "webhook_url": MY_WEBHOOK_URL,
        "metadata": {
            "auction_name": auction_name,
            "bidder_name": winner_name
        }
    }

    try:
        response = requests.post(EXTERNAL_BANK_URL, json=payload, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            Logger.error(f"Erro no Banco Externo: {response.text}")
            return None
    except Exception as e:
        Logger.error(f"Falha ao conectar no Banco Externo: {e}")
        return None


def handle_auction_winner(body_str: str):
    data = json.loads(body_str)
    auction_name = data.get("auction_name")
    winner_id = data.get("bidder_name")
    valor = data.get("bid_value")

    if winner_id == "Nenhum lance registrado":
        return

    Logger.info(f"Processando vencedor {winner_id} do leilão {auction_name} (R$ {valor})")

    bank_response = request_payment_link_external(auction_name, winner_id, valor)

    if bank_response:
        transacao_id = bank_response["transaction_id"]
        link = bank_response["payment_link"]

        payment_store[transacao_id] = {
            "auction_name": auction_name,
            "bidder_name": winner_id,
            "valor": valor,
            "status": "AGUARDANDO_PAGAMENTO"
        }

        Logger.success(f"Pagamento criado. Link externo: {link}")

        link_data = {
            "auction_name": auction_name,
            "bidder_name": winner_id,
            "bid_value": valor,
            "payment_link": link,
            "transacao_id": transacao_id,
        }
        notify_rabbit_mq(routing_key="link_pagamento", body=link_data)
    else:
        Logger.error("Não foi possível gerar link de pagamento.")

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


class WebhookData(BaseModel):
    transaction_id: str
    status: str
    amount: float
    metadata: dict


@asynccontextmanager
async def lifespan(app: FastAPI):
    consumer_thread = threading.Thread(target=start_rmq_consumer, daemon=True)
    consumer_thread.start()
    Logger.info("MS Pagamento: Consumidor RabbitMQ iniciado em background.")
    yield
    Logger.info("MS Pagamento: Encerrando.")


app = FastAPI(title="MS Pagamento", lifespan=lifespan)


@app.post("/webhook/pagamento")
def webhook_receiver(data: WebhookData):
    Logger.info(f"Webhook recebido para transação: {data.transaction_id} - Status: {data.status}")

    if data.transaction_id not in payment_store:
        Logger.warning("Webhook recebido de transação desconhecida!")
        raise HTTPException(status_code=404, detail="Transação não encontrada")

    local_data = payment_store[data.transaction_id]

    local_data["status"] = data.status

    status_msg = {
        "auction_name": local_data["auction_name"],
        "status": data.status,
        "bid_value": data.amount,
        "bidder_name": local_data["bidder_name"],
        "transacao_id": data.transaction_id
    }

    notify_rabbit_mq(routing_key="status_pagamento", body=status_msg)

    return {"status": "processed"}


if __name__ == "__main__":
    import uvicorn

    Logger.info("MS Pagamento rodando na porta 5003")
    uvicorn.run(app, host="0.0.0.0", port=5003)