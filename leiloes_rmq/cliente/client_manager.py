import threading
import pika
import time
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from leiloes_rmq.cliente.cliente import Cliente

name = input("Enter client name: ")
auctions_input = input("Enter auctions to subscribe (comma separated): ")
auctions = [a.strip() for a in auctions_input.split(",") if a.strip()]

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)
private_key_bytes = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)


def listen_and_subscribe():
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    cliente = Cliente(name, connection, channel)
    for auction in auctions:
        cliente.subscribe_to_auction(auction)
    cliente.start_listening()

def bid():
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    public_key = private_key.public_key()
    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    cliente = Cliente(name, connection, channel, private_key_bytes, public_key_bytes)
    for auction in auctions:
        cliente.subscribe_to_auction(auction)
    while True:
        auction = input("Enter auction name (or 'exit' to quit): ")
        if auction.lower() == "exit":
            break
        amount = input("Enter bid amount (integer): ")
        try:
            amount = int(amount)
            cliente.bid_to_auction(auction, amount)
        except ValueError:
            print("Invalid amount. Please enter a number.")

listen_thread = threading.Thread(target=listen_and_subscribe)
bid_thread = threading.Thread(target=bid)

listen_thread.start()
bid_thread.start()

listen_thread.join()
time.sleep(5)
bid_thread.join()