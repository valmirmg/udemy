import os

import pygame

from .botao import Botao
from .constants import (
    ALTURA,
    AZUL,
    BRANCO,
    CINZA_ESCURO,
    LARGURA,
    VERDE,
    VERMELHO,
)
from models.game import JogoPedraPapelTesoura


def carregar_e_recortar_imagens():
    base_dir = os.path.dirname(__file__)
    caminho_imagem = os.path.join(base_dir, "..", "img", "pedra-papel-tesoura.jpg")
    caminho_imagem = os.path.abspath(caminho_imagem)

    sprite = pygame.image.load(caminho_imagem).convert_alpha()
    largura_total, altura = sprite.get_size()
    largura_icone = largura_total // 3

    pedra_surface = sprite.subsurface((0, 0, largura_icone, altura)).copy()
    papel_surface = sprite.subsurface((largura_icone, 0, largura_icone, altura)).copy()
    tesoura_surface = sprite.subsurface(
        (2 * largura_icone, 0, largura_icone, altura)
    ).copy()

    return pedra_surface, papel_surface, tesoura_surface


class GameView:
    def __init__(self) -> None:
        pygame.display.set_caption("Pedra, Papel e Tesoura")
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))

        self.fonte_titulo = pygame.font.SysFont("arial", 56, bold=True)
        self.fonte_texto = pygame.font.SysFont("arial", 30)
        self.fonte_pequena = pygame.font.SysFont("arial", 22)

        img_pedra, img_papel, img_tesoura = carregar_e_recortar_imagens()

        # imagens grandes e bem visíveis (um pouco menores)
        altura_imagem = 160
        imagens_botoes_originais = [img_pedra, img_papel, img_tesoura]
        imagens_botoes = []
        larguras_imgs = []
        for img in imagens_botoes_originais:
            fator = altura_imagem / img.get_height()
            nova_largura = int(img.get_width() * fator)
            img_escalada = pygame.transform.smoothscale(
                img, (nova_largura, altura_imagem)
            )
            imagens_botoes.append(img_escalada)
            larguras_imgs.append(nova_largura)

        largura_max_img = max(larguras_imgs)
        padding_h = 40
        padding_v = 40
        largura_botao = largura_max_img + padding_h
        altura_botao = altura_imagem + padding_v
        espacamento = 50

        total_largura = largura_botao * 3 + espacamento * 2
        inicio_x = (LARGURA - total_largura) // 2

        # posição inicial (será ajustada em desenhar)
        y_botoes = ALTURA - altura_botao - 60

        cores = [AZUL, VERDE, VERMELHO]
        self.botoes: list[Botao] = []
        for i in range(3):
            x = inicio_x + i * (largura_botao + espacamento)
            botao = Botao(
                rect=(x, y_botoes, largura_botao, altura_botao),
                texto="",
                cor_fundo=cores[i],
                cor_hover=(
                    min(cores[i][0] + 30, 255),
                    min(cores[i][1] + 30, 255),
                    min(cores[i][2] + 30, 255),
                ),
                fonte=self.fonte_texto,
                imagem=imagens_botoes[i],
            )
            self.botoes.append(botao)

    def tratar_clique(self, evento) -> int | None:
        for i, botao in enumerate(self.botoes):
            if botao.foi_clicado(evento):
                return i
        return None

    def desenhar(self, jogo: JogoPedraPapelTesoura) -> None:
        self.tela.fill(BRANCO)

        # cabeçalho
        titulo = self.fonte_titulo.render(
            "Pedra, Papel e Tesoura", True, CINZA_ESCURO
        )
        titulo_rect = titulo.get_rect(center=(LARGURA // 2, 70))
        self.tela.blit(titulo, titulo_rect)

        instrucao = self.fonte_texto.render(
            "Clique em uma opção para jogar.", True, CINZA_ESCURO
        )
        instrucao_rect = instrucao.get_rect(center=(LARGURA // 2, 130))
        self.tela.blit(instrucao, instrucao_rect)

        # placar geral
        placar_texto = self.fonte_texto.render(
            f"Você: {jogo.placar.jogador}   Computador: {jogo.placar.computador}   Empates: {jogo.placar.empates}",
            True,
            CINZA_ESCURO,
        )
        placar_rect = placar_texto.get_rect(center=(LARGURA // 2, 190))
        self.tela.blit(placar_texto, placar_rect)

        # quadro central de resultado
        quadro_top = 210
        quadro_altura = 250
        pygame.draw.rect(
            self.tela,
            (255, 255, 255),
            (100, quadro_top, LARGURA - 200, quadro_altura),
            border_radius=20,
        )
        pygame.draw.rect(
            self.tela,
            CINZA_ESCURO,
            (100, quadro_top, LARGURA - 200, quadro_altura),
            2,
            border_radius=20,
        )

        # a partir do quadro, posicionamos os botões SEM sobrepor
        espacamento_quadro_botoes = 25
        y_botoes = quadro_top + quadro_altura + espacamento_quadro_botoes

        for i, botao in enumerate(self.botoes):
            x = botao.rect.x
            botao.rect.y = y_botoes

        if jogo.escolha_jogador is None:
            aviso = self.fonte_texto.render(
                "Nenhuma rodada jogada ainda.", True, CINZA_ESCURO
            )
            aviso_rect = aviso.get_rect(
                center=(LARGURA // 2, quadro_top + quadro_altura // 2)
            )
            self.tela.blit(aviso, aviso_rect)
        else:
            texto_jogador = self.fonte_texto.render(
                f"Sua escolha: {jogo.escolha_jogador}", True, AZUL
            )
            texto_comp = self.fonte_texto.render(
                f"Computador: {jogo.escolha_computador}", True, VERMELHO
            )
            texto_resultado = self.fonte_titulo.render(
                jogo.resultado,
                True,
                VERDE
                if jogo.resultado == "Você venceu!"
                else (
                    VERMELHO
                    if jogo.resultado == "Computador venceu!"
                    else CINZA_ESCURO
                ),
            )
            texto_placar_rodada = self.fonte_texto.render(
                f"Placar - Você: {jogo.placar.jogador}  Computador: {jogo.placar.computador}  Empates: {jogo.placar.empates}",
                True,
                CINZA_ESCURO,
            )

            # tudo encaixado confortavelmente dentro do quadro
            self.tela.blit(texto_jogador, (140, quadro_top + 20))
            self.tela.blit(texto_comp, (140, quadro_top + 65))

            resultado_rect = texto_resultado.get_rect(
                center=(LARGURA // 2, quadro_top + 145)
            )
            self.tela.blit(texto_resultado, resultado_rect)

            placar_rodada_rect = texto_placar_rodada.get_rect(
                center=(LARGURA // 2, quadro_top + 205)
            )
            self.tela.blit(texto_placar_rodada, placar_rodada_rect)

        dica = self.fonte_pequena.render(
            "Pressione R para limpar o resultado • ESC para sair",
            True,
            CINZA_ESCURO,
        )
        dica_rect = dica.get_rect(center=(LARGURA // 2, ALTURA - 25))
        self.tela.blit(dica, dica_rect)

        for botao in self.botoes:
            botao.desenhar(self.tela)

        pygame.display.flip()

