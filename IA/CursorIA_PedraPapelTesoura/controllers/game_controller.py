import sys

import pygame

from models.game import JogoPedraPapelTesoura
from views.constants import FPS
from views.ui import GameView


class GameController:
    def __init__(self) -> None:
        pygame.init()
        self.jogo = JogoPedraPapelTesoura()
        self.view = GameView()
        self.clock = pygame.time.Clock()
        self.rodando = True

    def executar(self) -> None:
        while self.rodando:
            self.clock.tick(FPS)

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.rodando = False
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        self.rodando = False
                    if evento.key == pygame.K_r:
                        self.jogo.limpar_rodada()
                else:
                    indice = self.view.tratar_clique(evento)
                    if indice is not None:
                        self.jogo.jogar(indice)

            self.view.desenhar(self.jogo)

        pygame.quit()
        sys.exit()

