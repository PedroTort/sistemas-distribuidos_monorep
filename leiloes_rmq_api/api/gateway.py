from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import AuctionModel, BidModel
from ms_lance.bid import Bid
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
async def create_item(auction_data: AuctionModel):
    if auction_data.name in [auction.name for auction in active_auctions]:
        return {"error": "Auction already exists"}
    auction = Auction(auction_data)
    response = auction.run_auction()
    if response.get("status_code") == 200:
        print("Auction created successfully")
        active_auctions.append(auction_data)
        auction_results[auction_data.name] = {
            "auction_name": auction_data.name,
            "bidder_name": "Nenhum lance registrado",
            "current_value": auction_data.current_value,
        }
    else:
        return {"error": {response.get("message")}}
    print(active_auctions)
    return auction_data


@app.post("/bid-auction")
async def post_bid_auction(bid: BidModel):
    Bid.handle_bid_made(active_auctions, auction_results, bid)
    return bid


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
