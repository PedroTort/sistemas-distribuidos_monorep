import time

import pika
import json
import threading
import httpx
import asyncio
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager
from sse_starlette.sse import EventSourceResponse
from typing import Dict
from terminal_logger import Logger
from fastapi.middleware.cors import CORSMiddleware

RABBITMQ_HOST = "localhost"
EXCHANGE_NAME = "auction"

MS_LEILAO_URL = "http://localhost:5001"
MS_LANCE_URL = "http://localhost:5002"

client_streams: Dict[str, asyncio.Queue] = {}
interesses: Dict[str, list] = {}

interest_lock = threading.Lock()
stream_lock = asyncio.Lock()


async def start_rmq_consumer_async(app: FastAPI):
    """Função wrapper para iniciar o consumidor síncrono em uma thread."""
    loop = asyncio.get_event_loop()
    app.state.event_loop = loop

    consumer_thread = threading.Thread(
        target=start_rmq_consumer, args=(app,), daemon=True
    )
    consumer_thread.start()
    Logger.info("Gateway: Consumidor RabbitMQ iniciado em background thread.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient()
    await start_rmq_consumer_async(app)

    yield

    await app.state.http_client.aclose()
    Logger.info("Gateway: Encerrando.")


app = FastAPI(title="API Gateway", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite o seu frontend React
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, DELETE, etc.)
    allow_headers=["*"],  # Permite todos os cabeçalhos
)

# --- Modelos Pydantic ---


class InterestRequest(BaseModel):
    client_id: str


# --- Endpoints REST (Proxy) ---


@app.post("/leiloes")
async def criar_leilao(request: Request):
    """Proxy para MS Leilão"""
    Logger.info("Gateway: Recebido POST /leiloes")
    try:
        data = await request.json()
        client = app.state.http_client
        response = await client.post(f"{MS_LEILAO_URL}/leiloes", json=data, timeout=10)
        return JSONResponse(content=response.json(), status_code=response.status_code)
    except httpx.HTTPStatusError as e:
        return JSONResponse(
            content=e.response.json(), status_code=e.response.status_code
        )
    except Exception as e:
        Logger.error(f"Gateway: Erro ao contatar MS Leilão: {e}")
        return JSONResponse(content={"erro": "MS Leilão indisponível"}, status_code=503)


@app.get("/leiloes/ativos")
async def consultar_leiloes_ativos():
    Logger.info("Gateway: Recebido GET /leiloes/ativos")
    try:
        client = app.state.http_client
        response = await client.get(f"{MS_LEILAO_URL}/leiloes/ativos", timeout=10)
        return JSONResponse(content=response.json(), status_code=response.status_code)
    except Exception as e:
        Logger.error(f"Gateway: Erro ao contatar MS Leilão: {e}")
        return JSONResponse(content={"erro": "MS Leilão indisponível"}, status_code=503)


@app.post("/lance")
async def efetuar_lance(request: Request):
    Logger.info("Gateway: Recebido POST /lances")
    try:
        data = await request.json()
        client = app.state.http_client
        response = await client.post(f"{MS_LANCE_URL}/lances", json=data, timeout=10)
        return JSONResponse(content=response.json(), status_code=response.status_code)
    except httpx.HTTPStatusError as e:
        print("e.response.status_code", e.response.status_code)
        return JSONResponse(
            content=e.response.json(), status_code=e.response.status_code
        )
    except Exception as e:
        Logger.error(f"Gateway: Erro ao contatar MS Lance: {e}")
        return JSONResponse(content={"erro": "MS Lance indisponível"}, status_code=503)


@app.post("/leiloes/{leilao_id}/registrar-interesse")
async def registrar_interesse(leilao_id: str, data: InterestRequest):
    client = app.state.http_client
    response = await client.get(f"{MS_LEILAO_URL}/leiloes/ativos", timeout=10)
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Leilão não encontrado ou inativo")

    if leilao_id not in [leilao["auction_name"] for leilao in response.json()]:
        raise HTTPException(status_code=404, detail="Leilão não encontrado ou inativo")

    with interest_lock:
        if leilao_id not in interesses:
            interesses[leilao_id] = []
        if data.client_id not in interesses[leilao_id]:
            interesses[leilao_id].append(data.client_id)

    Logger.info(f"Gateway: Cliente {data.client_id} registrou interesse em {leilao_id}")
    return {
        "status": "interesse registrado",
        "leilao": leilao_id,
        "cliente": data.client_id,
    }


@app.delete("/leiloes/{leilao_id}/cancelar-interesse")
def cancelar_interesse(leilao_id: str, data: InterestRequest):
    with interest_lock:
        if leilao_id in interesses and data.client_id in interesses[leilao_id]:
            interesses[leilao_id].remove(data.client_id)
            Logger.info(
                f"Gateway: Cliente {data.client_id} cancelou interesse em {leilao_id}"
            )
            return {"status": "interesse cancelado"}
    raise HTTPException(status_code=404, detail="Interesse não encontrado")


# --- Endpoint SSE (Async) ---


@app.get("/eventos/{client_id}")
async def sse_stream(request: Request, client_id: str):
    Logger.info(f"Gateway: Cliente {client_id} conectou ao stream SSE.")
    message_queue = asyncio.Queue()

    async with stream_lock:
        client_streams[client_id] = message_queue

    async def event_generator():
        try:
            while True:
                # Verifica se o cliente desconectou
                if await request.is_disconnected():
                    Logger.info(
                        f"Gateway: Cliente {client_id} desconectou (detectado)."
                    )
                    break

                # Espera por uma mensagem
                message_data = await message_queue.get()
                yield {"data": json.dumps(message_data)}
        except asyncio.CancelledError:
            Logger.info(f"Gateway: Conexão SSE para {client_id} cancelada.")
        finally:
            # Limpa a fila
            async with stream_lock:
                if client_id in client_streams:
                    del client_streams[client_id]
            Logger.info(f"Gateway: Fila de eventos para {client_id} removida.")

    return EventSourceResponse(event_generator())


# --- Consumidor RabbitMQ (Lógica de Broadcast) ---


def broadcast_message(app: FastAPI, message_data: dict, routing_key: str):
    Logger.info(f"Gateway: Recebido do RMQ '{routing_key}'. Roteando para SSE...")
    target_clients = set()
    leilao_id = message_data.get("auction_name")
    bidder_name = message_data.get("bidder_name") or message_data.get("cliente")

    message_data["event_type"] = routing_key
    loop = app.state.event_loop

    with interest_lock:
        if routing_key in ["lance_validado", "leilao_vencedor"]:
            if routing_key == "lance_validado":
                new_value = message_data.get("bid_value")
                if leilao_id and new_value is not None:
                    print("Agendando atualização de valor do leilão...")
                    client = app.state.http_client
                    asyncio.run_coroutine_threadsafe(
                        atualizar_valor_leilao(client, leilao_id, new_value), loop
                    )
            if leilao_id in interesses:
                target_clients.update(interesses[leilao_id])

        elif routing_key in ["lance_invalidado", "link_pagamento", "status_pagamento"]:
            if bidder_name:
                target_clients.add(bidder_name)

    for client_id in target_clients:
        if client_id in client_streams:
            queue = client_streams[client_id]
            asyncio.run_coroutine_threadsafe(queue.put(message_data), loop)
            Logger.info(f"Gateway: Enviando SSE '{routing_key}' para {client_id}")


def start_rmq_consumer(app: FastAPI):
    Logger.info("Gateway: Iniciando lógica do consumidor RabbitMQ...")
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
        channel = connection.channel()
        channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="direct")

        routing_keys = [
            "lance_validado",
            "lance_invalidado",
            "leilao_vencedor",
            "link_pagamento",
            "status_pagamento",
        ]

        queue_name = "api_gateway_listener"
        channel.queue_declare(queue=queue_name, durable=True, exclusive=False)

        for rk in routing_keys:
            channel.queue_bind(exchange=EXCHANGE_NAME, queue=queue_name, routing_key=rk)

        def rmq_callback(ch, method, properties, body):
            try:
                message_data = json.loads(body.decode("utf-8"))
                broadcast_message(app, message_data, method.routing_key)
            except Exception as e:
                Logger.error(f"Gateway: Erro ao processar msg RMQ: {e}")
            ch.basic_ack(delivery_tag=method.delivery_tag)

        channel.basic_consume(
            queue=queue_name, on_message_callback=rmq_callback, auto_ack=False
        )
        channel.start_consuming()

    except pika.exceptions.AMQPConnectionError:
        Logger.error(
            "Gateway: Não foi possível conectar ao RabbitMQ. Reiniciando em 5s..."
        )
        time.sleep(5)
        start_rmq_consumer(app)
    except Exception as e:
        Logger.error(f"Gateway: Consumidor RMQ falhou: {e}")
    finally:
        if "connection" in locals() and connection.is_open:
            connection.close()
        Logger.info("Gateway: Consumidor RabbitMQ encerrado.")


async def atualizar_valor_leilao(
    client: httpx.AsyncClient, auction_name: str, new_value: float
):

    Logger.info(
        f"Gateway: Atualizando valor do leilão {auction_name} para {new_value} no MS Leilão..."
    )

    try:
        url = f"{MS_LEILAO_URL}/leiloes/{auction_name}/valor"
        payload = {"new_value": new_value}
        response = await client.put(url, json=payload, timeout=5)

        if response.status_code == 200:
            Logger.info(
                f"Gateway: Valor do leilão {auction_name} atualizado para {new_value} no MS Leilão."
            )
        else:
            Logger.warning(
                f"Gateway: Falha ao atualizar valor do leilão {auction_name}. MS Leilão Status: {response.status_code}"
            )
    except Exception as e:
        Logger.error(f"Gateway: Erro ao chamar MS Leilão para atualizar valor: {e}")


if __name__ == "__main__":
    import uvicorn

    Logger.info("API Gateway (FastAPI/SSE) iniciando na porta 5000.")
    uvicorn.run(app, host="0.0.0.0", port=5000)
