from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta

from ms_leilao.auction_lifecycle import AuctionLifecycle
from terminal_logger import Logger
from typing import List, Dict, Any

app = FastAPI(title="MS Leilão")

leiloes_db: Dict[str, Any] = {}
leilao_threads: Dict[str, AuctionLifecycle] = {}


class AuctionCreate(BaseModel):
    auction_name: str
    description: str
    current_value: float
    start_date: datetime
    end_date: datetime


class AuctionInfo(BaseModel):
    auction_name: str
    description: str
    start_date: datetime
    end_date: datetime
    current_value: float
    status: str


class ActiveAuctionInfo(BaseModel):
    auction_name: str
    description: str
    current_value: float
    start_date: datetime
    end_date: datetime


class AuctionUpdateValue(BaseModel):
    new_value: float


# --- Endpoints ---


@app.post("/leiloes", response_model=AuctionInfo, status_code=201)
def criar_leilao(dados: AuctionCreate, background_tasks: BackgroundTasks):
    Logger.info(f"Recebida requisição para criar leilão: {dados.auction_name}")

    auction_name = dados.auction_name
    if auction_name in leiloes_db:
        raise HTTPException(status_code=400, detail="Leilão com este nome já existe")

    if dados.end_date <= dados.start_date:
        raise HTTPException(
            status_code=400, detail="Data/hora de término deve ser após o início"
        )

    # Armazena a definição do leilão
    leilao_info = AuctionInfo(
        auction_name=auction_name,
        description=dados.description,
        start_date=dados.start_date,
        end_date=dados.end_date,
        current_value=dados.current_value,
        status="nao_iniciado",
    )
    leiloes_db[auction_name] = leilao_info.model_dump()  # Armazena como dict
    # Inicia a thread do ciclo de vida do leilão
    lifecycle_thread = AuctionLifecycle(
        auction_name=auction_name,
        description=dados.description,
        start_date=dados.start_date,
        end_date=dados.end_date,
        current_value=dados.current_value,
    )
    # Usamos start() pois é uma Thread, não uma task de background do FastAPI
    lifecycle_thread.start()
    leilao_threads[auction_name] = lifecycle_thread

    Logger.success(f"Leilão {auction_name} criado e agendado.")
    return leilao_info


@app.get("/leiloes/ativos", response_model=List[ActiveAuctionInfo])
def consultar_leiloes_ativos():
    Logger.info("Recebida requisição para consultar leilões ativos.")

    now = datetime.now(timezone(timedelta(hours=-3)))
    ativos = []
    for auction_name, leilao in leiloes_db.items():
        start_date = leilao["start_date"]
        end_date = leilao["end_date"]

        status = "nao_iniciado"
        if now >= start_date:
            status = "ativo"
        if now >= end_date:
            status = "encerrado"

        leiloes_db[auction_name]["status"] = status

        if status == "ativo":
            ativos.append(
                ActiveAuctionInfo(
                    auction_name=leilao["auction_name"],
                    description=leilao["description"],
                    current_value=leilao["current_value"],
                    start_date=start_date,
                    end_date=end_date,
                )
            )

    return ativos


@app.put("/leiloes/{auction_name}/valor", response_model=AuctionInfo)
def atualizar_valor_leilao(auction_name: str, data: AuctionUpdateValue):
    Logger.info(f"Recebida requisição para atualizar valor do leilão: {auction_name}")

    if auction_name not in leiloes_db:
        Logger.error(
            f"MS Leilão: Tentativa de atualizar leilão inexistente: {auction_name}"
        )
        raise HTTPException(status_code=404, detail="Leilão não encontrado")

    leilao = leiloes_db[auction_name]

    # Atualiza o valor usando o dado do modelo Pydantic
    leilao["current_value"] = data.new_value

    Logger.success(f"Leilão {auction_name} atualizado para valor {data.new_value}.")

    # Retorna o objeto completo do leilão atualizado
    return AuctionInfo(**leilao)


if __name__ == "__main__":
    import uvicorn

    Logger.info("MS Leilão (FastAPI) iniciando na porta 5001.")
    uvicorn.run(app, host="0.0.0.0", port=5001)
