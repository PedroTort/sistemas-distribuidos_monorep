class TerminalColors:
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BOLD = "\033[1m"


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
        print(f"{TerminalColors.GREEN}[LANCE VALIDADO]{TerminalColors.RESET} {message}")

    @staticmethod
    def auction_winner(message: str):
        print(f"{TerminalColors.MAGENTA}[VENCEDOR]{TerminalColors.RESET} {message}")
