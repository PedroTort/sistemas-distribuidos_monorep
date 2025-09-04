import threading
import pika
from leiloes_rmq.cliente.cliente import Cliente

name = input("Enter client name: ")
auctions_input = input("Enter auctions to subscribe (comma separated): ")
auctions = [a.strip() for a in auctions_input.split(",") if a.strip()]

def listen_and_subscribe():
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    cliente = Cliente(name, connection, channel)
    for auction in auctions:
        cliente.subscribe_to_auction(auction)
    cliente.start_listening()
    connection.close()

def bid():
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    cliente = Cliente(name, connection, channel)
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
bid_thread.join()