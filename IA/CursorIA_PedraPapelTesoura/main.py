import sys
import random

import pygame


LARGURA = 800
ALTURA = 600
FPS = 60

BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
CINZA_CLARO = (220, 220, 220)
CINZA_ESCURO = (60, 60, 60)
VERDE = (46, 204, 113)
VERMELHO = (231, 76, 60)
AZUL = (52, 152, 219)

OPCOES = ["Pedra", "Papel", "Tesoura"]


class Botao:
    def __init__(self, rect, texto, cor_fundo, cor_hover, fonte):
        self.rect = pygame.Rect(rect)
        self.texto = texto
        self.cor_fundo = cor_fundo
        self.cor_hover = cor_hover
        self.fonte = fonte

    def desenhar(self, superficie):
        mouse_pos = pygame.mouse.get_pos()
        esta_hover = self.rect.collidepoint(mouse_pos)
        cor = self.cor_hover if esta_hover else self.cor_fundo

        pygame.draw.rect(superficie, cor, self.rect, border_radius=10)
        pygame.draw.rect(superficie, CINZA_ESCURO, self.rect, 2, border_radius=10)

        texto_render = self.fonte.render(self.texto, True, PRETO)
        texto_rect = texto_render.get_rect(center=self.rect.center)
        superficie.blit(texto_render, texto_rect)

    def foi_clicado(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect.collidepoint(evento.pos):
                return True
        return False


def determinar_resultado(jogador, computador):
    if jogador == computador:
        return "Empate"

    if (
        (jogador == "Pedra" and computador == "Tesoura")
        or (jogador == "Papel" and computador == "Pedra")
        or (jogador == "Tesoura" and computador == "Papel")
    ):
        return "Você venceu!"

    return "Computador venceu!"


def main():
    pygame.init()
    pygame.display.set_caption("Pedra, Papel e Tesoura")
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    clock = pygame.time.Clock()

    fonte_titulo = pygame.font.SysFont("arial", 48, bold=True)
    fonte_texto = pygame.font.SysFont("arial", 28)
    fonte_pequena = pygame.font.SysFont("arial", 22)

    largura_botao = 180
    altura_botao = 70
    espacamento = 40
    y_botoes = ALTURA - 150

    total_largura = largura_botao * 3 + espacamento * 2
    inicio_x = (LARGURA - total_largura) // 2

    botoes = []
    cores = [AZUL, VERDE, VERMELHO]

    for i, opcao in enumerate(OPCOES):
        x = inicio_x + i * (largura_botao + espacamento)
        botao = Botao(
            rect=(x, y_botoes, largura_botao, altura_botao),
            texto=opcao,
            cor_fundo=cores[i],
            cor_hover=(min(cores[i][0] + 30, 255),
                       min(cores[i][1] + 30, 255),
                       min(cores[i][2] + 30, 255)),
            fonte=fonte_texto,
        )
        botoes.append(botao)

    escolha_jogador = None
    escolha_computador = None
    resultado = ""
    placar_jogador = 0
    placar_computador = 0
    empates = 0

    rodando = True
    while rodando:
        clock.tick(FPS)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    rodando = False
                if evento.key == pygame.K_r:
                    escolha_jogador = None
                    escolha_computador = None
                    resultado = ""
            else:
                for i, botao in enumerate(botoes):
                    if botao.foi_clicado(evento):
                        escolha_jogador = OPCOES[i]
                        escolha_computador = random.choice(OPCOES)
                        resultado = determinar_resultado(escolha_jogador, escolha_computador)

                        if resultado == "Você venceu!":
                            placar_jogador += 1
                        elif resultado == "Computador venceu!":
                            placar_computador += 1
                        else:
                            empates += 1

        tela.fill((245, 246, 250))

        titulo = fonte_titulo.render("Pedra, Papel e Tesoura", True, CINZA_ESCURO)
        titulo_rect = titulo.get_rect(center=(LARGURA // 2, 60))
        tela.blit(titulo, titulo_rect)

        instrucao = fonte_texto.render("Clique em uma opção para jogar.", True, CINZA_ESCURO)
        instrucao_rect = instrucao.get_rect(center=(LARGURA // 2, 120))
        tela.blit(instrucao, instrucao_rect)

        placar_texto = fonte_texto.render(
            f"Você: {placar_jogador}   Computador: {placar_computador}   Empates: {empates}",
            True,
            CINZA_ESCURO,
        )
        placar_rect = placar_texto.get_rect(center=(LARGURA // 2, 170))
        tela.blit(placar_texto, placar_rect)

        pygame.draw.rect(tela, BRANCO, (100, 210, LARGURA - 200, 220), border_radius=15)
        pygame.draw.rect(tela, CINZA_ESCURO, (100, 210, LARGURA - 200, 220), 2, border_radius=15)

        if escolha_jogador is None:
            aviso = fonte_texto.render("Nenhuma rodada jogada ainda.", True, CINZA_ESCURO)
            aviso_rect = aviso.get_rect(center=(LARGURA // 2, 320))
            tela.blit(aviso, aviso_rect)
        else:
            texto_jogador = fonte_texto.render(f"Sua escolha: {escolha_jogador}", True, AZUL)
            texto_comp = fonte_texto.render(f"Computador: {escolha_computador}", True, VERMELHO)
            texto_resultado = fonte_titulo.render(resultado, True, VERDE if resultado == "Você venceu!" else (VERMELHO if resultado == "Computador venceu!" else CINZA_ESCURO))

            tela.blit(texto_jogador, (140, 240))
            tela.blit(texto_comp, (140, 290))

            resultado_rect = texto_resultado.get_rect(center=(LARGURA // 2, 360))
            tela.blit(texto_resultado, resultado_rect)

        dica = fonte_pequena.render("Pressione R para limpar o resultado • ESC para sair", True, CINZA_ESCURO)
        dica_rect = dica.get_rect(center=(LARGURA // 2, ALTURA - 40))
        tela.blit(dica, dica_rect)

        for botao in botoes:
            botao.desenhar(tela)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

