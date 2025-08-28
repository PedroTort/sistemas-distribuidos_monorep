from enum import Enum

class QueueNames(Enum):
    LEILAO = "leilao"
    LEILAO_INICIADO = "leilao_iniciado"
    LEILAO_FINALIZADO = "leilao_finalizado"
    LANCE_REALIZADO = "lance_realizado"
    LANCE_VALIDADO = "lance_validado"
    LANCE_VENCEDOR = "lance_vencedor"
    LEILAO_1 = "leilao_1"
    LEILAO_2 = "leilao_2"