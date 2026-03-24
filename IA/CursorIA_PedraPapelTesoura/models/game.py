import random
from dataclasses import dataclass


OPCOES = ["Pedra", "Papel", "Tesoura"]


@dataclass
class Placar:
    jogador: int = 0
    computador: int = 0
    empates: int = 0


class JogoPedraPapelTesoura:
    def __init__(self) -> None:
        self.escolha_jogador: str | None = None
        self.escolha_computador: str | None = None
        self.resultado: str = ""
        self.placar = Placar()

    def limpar_rodada(self) -> None:
        self.escolha_jogador = None
        self.escolha_computador = None
        self.resultado = ""

    def jogar(self, indice_escolha: int) -> None:
        """Realiza uma jogada a partir do índice do botão clicado."""
        if indice_escolha < 0 or indice_escolha >= len(OPCOES):
            return

        self.escolha_jogador = OPCOES[indice_escolha]
        self.escolha_computador = random.choice(OPCOES)
        self.resultado = self._determinar_resultado()
        self._atualizar_placar()

    def _determinar_resultado(self) -> str:
        jogador = self.escolha_jogador
        computador = self.escolha_computador

        if jogador is None or computador is None:
            return ""

        if jogador == computador:
            return "Empate"

        if (
            (jogador == "Pedra" and computador == "Tesoura")
            or (jogador == "Papel" and computador == "Pedra")
            or (jogador == "Tesoura" and computador == "Papel")
        ):
            return "Você venceu!"

        return "Computador venceu!"

    def _atualizar_placar(self) -> None:
        if self.resultado == "Você venceu!":
            self.placar.jogador += 1
        elif self.resultado == "Computador venceu!":
            self.placar.computador += 1
        elif self.resultado == "Empate":
            self.placar.empates += 1

