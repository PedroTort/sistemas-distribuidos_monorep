import uvicorn
import uuid
import httpx
import asyncio
from fastapi import FastAPI, BackgroundTasks, Request
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Sistema Bancário Externo (Mock)")

transactions_db = {}

class PaymentCreate(BaseModel):
    amount: float
    currency: str = "BRL"
    client_name: str
    webhook_url: str
    metadata: Optional[dict] = {}


@app.post("/api/payments")
def create_payment(payment: PaymentCreate):
    transaction_id = str(uuid.uuid4())

    transactions_db[transaction_id] = {
        "status": "PENDING",
        "amount": payment.amount,
        "client": payment.client_name,
        "webhook_url": payment.webhook_url,
        "metadata": payment.metadata
    }

    checkout_link = f"http://localhost:5004/checkout/{transaction_id}"

    print(f"[BANCO] Transação criada: {transaction_id}. Link: {checkout_link}")

    return {
        "transaction_id": transaction_id,
        "payment_link": checkout_link,
        "status": "PENDING"
    }


async def send_webhook(url: str, payload: dict):
    async with httpx.AsyncClient() as client:
        print(f"[BANCO] Enviando webhook para {url}...")
        try:
            await client.post(url, json=payload)
            print(f"[BANCO] Webhook entregue com sucesso.")
        except Exception as e:
            print(f"[BANCO] Falha ao entregar webhook: {e}")


@app.get("/checkout/{transaction_id}")
async def fake_checkout_page(transaction_id: str, background_tasks: BackgroundTasks):
    if transaction_id not in transactions_db:
        return {"error": "Transação não encontrada"}

    tx = transactions_db[transaction_id]

    tx["status"] = "APPROVED"

    webhook_payload = {
        "transaction_id": transaction_id,
        "status": "aprovado",
        "amount": tx["amount"],
        "metadata": tx["metadata"]
    }

    background_tasks.add_task(send_webhook, tx["webhook_url"], webhook_payload)

    return {
        "message": "Pagamento realizado com sucesso no Banco Externo!",
        "transaction_id": transaction_id,
        "status": "APPROVED",
        "info": "O MS Pagamento foi notificado via Webhook."
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5004)