import threading
import time
import pika
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from leiloes_rmq.terminal_logger import Logger
from leiloes_rmq.client.client import Client

Logger.input_prompt("Nome do cliente:")
name = input().strip()
Logger.input_prompt("Leiloes para participar (separados por virgula):")
auctions_input = input().lower()
auctions = [a.strip() for a in auctions_input.split(",")]

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)
private_key_bytes = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)


def listen_and_subscribe():
    type_name = "listener"
    client = Client(name, type_name)
    for auction in auctions:
        client.subscribe_to_auction(auction)
        time.sleep(1)

    client.start_listening()


def bid():
    public_key = private_key.public_key()
    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    type_name = "bidder"
    client = Client(name, type_name, private_key_bytes, public_key_bytes)
    for auction in auctions:
        client.subscribe_to_auction(auction)
        time.sleep(1)
    while True:
        time.sleep(1)
        Logger.input_prompt("Nome do leilão para fazer o lance:")
        auction = input().lower()
        Logger.input_prompt("Valor do lance (número):")
        amount = input()
        # amount = input("Valor do lance (número): ")
        try:
            amount = int(amount)
            client.bid_to_auction(auction, amount)
        except ValueError:
            Logger.error("Valor inválido. Por favor, digite um número.")


listen_thread = threading.Thread(target=listen_and_subscribe)
bid_thread = threading.Thread(target=bid)

listen_thread.start()
bid_thread.start()

listen_thread.join()
time.sleep(5)
bid_thread.join()
