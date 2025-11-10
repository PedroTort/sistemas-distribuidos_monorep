import pika
import json
import threading
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from terminal_logger import Logger, MessageFormatter

RABBITMQ_HOST = "localhost"
EXCHANGE_NAME = "auction"

active_auctions = []
auction_results = {}
lock = threading.Lock()


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
        Logger.info(f"Publicado '{routing_key}' para o leilão {body.get('auction_name')}")
        connection.close()
    except Exception as e:
        Logger.error(f"Erro ao publicar no RabbitMQ: {e}")


def handle_auction_started(body_str: str):
    body = json.loads(body_str)
    print(body)
    auction_name = body.get("auction_name")
    valor_inicial = body.get("valor_inicial", 0)

    with lock:
        if auction_name not in active_auctions:
            active_auctions.append(auction_name)
            auction_results[auction_name] = {
                "auction_name": auction_name,
                "cliente": "Nenhum lance registrado",
                "bid_value": valor_inicial,
            }
            Logger.auction_started(f"Leilão {auction_name} agora ativo no MS Lance!")


def handle_auction_finished(body_str: str):
    body = json.loads(body_str)
    auction_name = body.get("auction_name")

    with lock:
        if auction_name in active_auctions:
            winner_data = auction_results.get(auction_name)
            notify_rabbit_mq(routing_key="leilao_vencedor", body=winner_data)
            active_auctions.remove(auction_name)
            message = MessageFormatter.auction_ended(auction_name, winner_data["cliente"], winner_data["bid_value"])
            Logger.auction_ended(message)


def start_rmq_consumer():
    Logger.info("Iniciando consumidor RabbitMQ para MS Lance...")
    connection, channel = get_pika_connection_channel()

    queues_to_consume = {
        "leilao_iniciado": handle_auction_started,
        "leilao_finalizado": handle_auction_finished
    }

    queue_name = "ms_lance_lifecycle_listener"
    channel.queue_declare(queue=queue_name, durable=True)

    for routing_key in queues_to_consume.keys():
        channel.queue_bind(
            exchange=EXCHANGE_NAME, queue=queue_name, routing_key=routing_key
        )

    def rmq_callback(ch, method, properties, body):
        Logger.info(f"MS Lance recebeu evento: {method.routing_key}")
        callback_handler = queues_to_consume.get(method.routing_key)
        if callback_handler:
            try:
                callback_handler(body.decode("utf-8"))
            except Exception as e:
                Logger.error(f"Erro ao processar {method.routing_key}: {e}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=queue_name, on_message_callback=rmq_callback, auto_ack=False)

    try:
        channel.start_consuming()
    except Exception as e:
        Logger.error(f"Consumidor RMQ MS-Lance parou: {e}")
    finally:
        connection.close()
        Logger.info("Consumidor RabbitMQ do MS Lance encerrado.")


# --- API FastAPI ---

class BidCreate(BaseModel):
    auction_name: str
    user_id: str
    bid_value: float


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicia o consumidor RMQ em uma thread daemon
    consumer_thread = threading.Thread(target=start_rmq_consumer, daemon=True)
    consumer_thread.start()
    Logger.info("MS Lance: Consumidor RabbitMQ iniciado em background.")
    yield
    Logger.info("MS Lance: Encerrando.")


app = FastAPI(title="MS Lance", lifespan=lifespan)


@app.post("/lances")
def efetuar_lance(new_bid: BidCreate):
    """
    Recebe um lance via REST do API Gateway.
    """
    Logger.info(f"Recebido lance de {new_bid.user_id} para {new_bid.auction_name} no valor de {new_bid.bid_value}")

    with lock:
        if new_bid.auction_name in active_auctions:
            current_bid = auction_results[new_bid.auction_name]

            if new_bid.bid_value > current_bid["bid_value"]:
                new_bid_data = {
                    "auction_name": new_bid.auction_name,
                    "cliente": new_bid.user_id,
                    "bid_value": new_bid.bid_value
                }
                auction_results[new_bid.auction_name] = new_bid_data

                notify_rabbit_mq(routing_key="lance_validado", body=new_bid_data)

                message = MessageFormatter.bid_validated(new_bid.auction_name, new_bid.user_id, new_bid.bid_value)
                Logger.bid_validated(message)
                return {"status": "lance_aceito", "data": new_bid_data}
            else:
                # Lance INVÁLIDO (valor baixo)
                motivo = f"Lance R$ {new_bid.bid_value} não é maior que o lance atual R$ {current_bid['bid_value']}."
                invalid_data = {
                    "auction_name": new_bid.auction_name,
                    "user_id": new_bid.user_id,
                    "bid_value": new_bid.bid_value,
                    "motivo": motivo
                }
                notify_rabbit_mq(routing_key="lance_invalidado", body=invalid_data)
                Logger.error(motivo)
                raise HTTPException(status_code=400, detail=motivo)
        else:
            # Lance INVÁLIDO (leilão inativo)
            motivo = "Leilão não está ativo."
            invalid_data = {
                "auction_name": new_bid.auction_name,
                "user_id": new_bid.user_id,
                "bid_value": new_bid.bid_value,
                "motivo": motivo
            }
            notify_rabbit_mq(routing_key="lance_invalidado", body=invalid_data)
            Logger.error(motivo)
            raise HTTPException(status_code=400, detail=motivo)


if __name__ == "__main__":
    import uvicorn

    Logger.info("MS Lance (FastAPI) iniciando na porta 5002.")
    uvicorn.run(app, host="0.0.0.0", port=5002)