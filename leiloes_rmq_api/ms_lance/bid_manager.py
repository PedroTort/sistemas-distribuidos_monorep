import pika
from ms_lance.bid import Bid



lance = Bid(connection, channel)
lance.start_listening()

connection.close()
