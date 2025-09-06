class TerminalColors:
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    LIGHT_GREEN = "\033[92m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    GRAY = "\033[90m"
    ORANGE = "\033[38;5;208m"
    BOLD = "\033[1m"


class MessageFormatter:
    @staticmethod
    def auction_started(auction_id, description, start_time, end_time):
        return (
            f"📢 LEILÃO '{auction_id}' INICIADO! 📢\n"
            f"   Descrição: {TerminalColors.CYAN}{description}{TerminalColors.RESET}\n"
            f"   Início: {start_time}\n"
            f"   Término: {end_time}"
        )

    @staticmethod
    def auction_ended(auction_id, winner_name, bid_value):
        return (
            f"Leilão {TerminalColors.BOLD}{auction_id}{TerminalColors.RESET} finalizado:\n"
            f"   Vencedor: {TerminalColors.CYAN}{winner_name}{TerminalColors.RESET}\n"
            f"   Valor do lance: {TerminalColors.GREEN}{bid_value}{TerminalColors.RESET}"
        )

    @staticmethod
    def bid_validated(auction_id, client, bid_value):
        return (
            f"Lance validado enviado para o leilão {TerminalColors.BOLD}{auction_id}{TerminalColors.RESET}\n"
            f"   Cliente: {TerminalColors.CYAN}{client}{TerminalColors.RESET}\n"
            f"   Valor do lance: {TerminalColors.LIGHT_GREEN}{bid_value}{TerminalColors.RESET}"
        )

    @staticmethod
    def new_bid_notification(routing_key, auction_id, client, bid_value):
        return (
            f"Nova informação da {TerminalColors.BOLD}{routing_key}{TerminalColors.RESET} recebida:\n"
            f"   Leilão: {TerminalColors.CYAN}{auction_id}{TerminalColors.RESET}\n"
            f"   Cliente: {TerminalColors.MAGENTA}{client}{TerminalColors.RESET}\n"
            f"   Valor do lance: {TerminalColors.GREEN}{bid_value}{TerminalColors.RESET}"
        )

    @staticmethod
    def auction_winner(auction_id, client, bid_value):
        return (
            f"Resultado do leilão {TerminalColors.BOLD}{auction_id}{TerminalColors.RESET}:\n"
            f"   Vencedor: {TerminalColors.CYAN}{client}{TerminalColors.RESET}\n"
            f"   Valor do lance: {TerminalColors.GREEN}{bid_value}{TerminalColors.RESET}"
        )


class Logger:
    @staticmethod
    def info(message: str):
        print(f"{TerminalColors.YELLOW}[INFO]{TerminalColors.RESET} {message}")

    @staticmethod
    def error(message: str):
        print(f"{TerminalColors.RED}[ERRO]{TerminalColors.RESET} {message}")

    @staticmethod
    def success(message: str):
        print(f"{TerminalColors.GREEN}[SUCESSO]{TerminalColors.RESET} {message}")

    @staticmethod
    def input_prompt(message: str):
        print(f"{TerminalColors.MAGENTA}[INPUT]{TerminalColors.RESET} {message}")

    @staticmethod
    def auction_started(message: str):
        print(f"{TerminalColors.BLUE}[LEILÃO INICIADO]{TerminalColors.RESET} {message}")

    @staticmethod
    def auction_ended(message: str):
        print(
            f"{TerminalColors.CYAN}[LEILÃO FINALIZADO]{TerminalColors.RESET} {message}"
        )

    @staticmethod
    def bid_placed(message: str):
        print(
            f"{TerminalColors.GREEN}[LANCE REALIZADO]{TerminalColors.RESET} {message}"
        )

    @staticmethod
    def bid_validated(message: str):
        print(
            f"{TerminalColors.LIGHT_GREEN}[LANCE VALIDADO]{TerminalColors.RESET} {message}"
        )

    @staticmethod
    def auction_winner(message: str):
        print(f"{TerminalColors.MAGENTA}[VENCEDOR]{TerminalColors.RESET} {message}")
