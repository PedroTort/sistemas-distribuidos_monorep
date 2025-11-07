import threading
from ms_leilao.auction import Auction
from terminal_logger import Logger

DEFAULT_DURATION = 30

if __name__ == "__main__":
    Logger.input_prompt(
        f"Duração do leilão 1 em segundos (padrão {DEFAULT_DURATION}): "
    )
    dur1 = input()
    Logger.input_prompt(
        f"Duração do leilão 2 em segundos (padrão {DEFAULT_DURATION}): "
    )
    dur2 = input()

    dur1 = int(dur1) if dur1.strip() else DEFAULT_DURATION
    dur2 = int(dur2) if dur2.strip() else DEFAULT_DURATION

    auction_one = Auction("leilao_1", "Super leilao 1", dur1)
    auction_two = Auction("leilao_2", "Super leilao 2", dur2)

    t1 = threading.Thread(target=auction_one.start_auction)
    t2 = threading.Thread(target=auction_two.start_auction)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    auction_one.connection.close()
    auction_two.connection.close()

    Logger.info("Todos os leilões finalizados e conexões encerradas.")
