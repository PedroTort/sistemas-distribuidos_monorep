from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import AuctionModel
from ms_leilao.auction import Auction

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

active_auctions = []
auction_results = {}

@app.get("/")
async def root():
    return {"message": "Opa"}


@app.get("/get-auctions")
async def get_auctions():
    return active_auctions


@app.post("/create-auction")
async def create_item(auction: AuctionModel):
    if auction.name in active_auctions:
        return  {"error": "Auction already exists"}
    auction = Auction(auction)
    response = auction.run_auction()
    if response.get("status_code") == 200:
        active_auctions.append(auction)
    return auction

#
# @app.post("/bid-auction")
# async def post_bid_auction(bid: Bid):
#     if bid.auction_name not in [auction.name for auction in array_auctions]:
#         return {"error": "Auction not found"}
#     array_bids.append(bid)
#     print(array_bids)
#     return bid
#
#
# @app.post("/subscribe-auction")
# async def post_subscribe_auction(subscribe_to_auction: AuctionSubscription):
#     if subscribe_to_auction.auction_name not in [
#         auction.name for auction in array_auctions
#     ]:
#         return {"error": "Auction not found"}
#     array_subscriber_auctions.append(subscribe_to_auction)
#     print(
#         subscribe_to_auction.auction_name
#         + " subscribed by "
#         + subscribe_to_auction.subscriber_name
#     )
#
#
# # futuramente vai ser um post (?)
# @app.patch("/unsubscribe-auction")
# async def patch_unsubscribe_auction(unsubscribe_to_auction: AuctionSubscription):
#     if unsubscribe_to_auction.auction_name not in [
#         auction.name for auction in array_auctions
#     ]:
#         return {"error": "Auction not found"}
#     array_subscriber_auctions.remove(unsubscribe_to_auction)
#     print(
#         unsubscribe_to_auction.subscriber_name
#         + " unsubscribed from "
#         + unsubscribe_to_auction.auction_name
#     )
