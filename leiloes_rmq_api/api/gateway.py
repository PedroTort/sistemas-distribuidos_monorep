from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware



class Auction(BaseModel):
    name: str
    description: str | None = None
    current_value: float
    start_date: datetime
    end_date: datetime

class Bid(BaseModel):
    auction_name: str
    bidder_name: str
    bid_value: float
    bid_time: datetime

class AuctionSubscription(BaseModel):
    auction_name: str
    subscriber_name: str


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"], 
    allow_headers=["*"],     
)

array_auctions = []
array_bids = []
array_subscriber_auctions = []

@app.get("/")
async def root():
    return {"message": "Opa"}

@app.get("/get-auctions")
async def get_auctions():
    return array_auctions

@app.post("/create-auction")
async def create_item(auction: Auction):
    print("to sendo chamado ein")
    array_auctions.append(auction)
    return auction

@app.post("/bid-auction")
async def post_bid_auction(bid: Bid):
    if(bid.auction_name not in [ auction.name for auction in array_auctions ]):
        return {"error": "Auction not found"}
    array_bids.append(bid)
    print( array_bids )
    return bid

@app.post("/subscribe-auction")
async def post_subscribe_auction(subscribe_to_auction: AuctionSubscription):
    if(subscribe_to_auction.auction_name not in [ auction.name for auction in array_auctions ]):
        return {"error": "Auction not found"}
    array_subscriber_auctions.append(subscribe_to_auction)
    print( subscribe_to_auction.auction_name + " subscribed by " + subscribe_to_auction.subscriber_name )

# futuramente vai ser um post (?)
@app.patch("/unsubscribe-auction")
async def patch_unsubscribe_auction(unsubscribe_to_auction: AuctionSubscription):
    if(unsubscribe_to_auction.auction_name not in [ auction.name for auction in array_auctions ]):
        return {"error": "Auction not found"}
    array_subscriber_auctions.remove(unsubscribe_to_auction)
    print( unsubscribe_to_auction.subscriber_name + " unsubscribed from " +   unsubscribe_to_auction.auction_name)