import sys
import random
import os

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
    def __init__(self, rect, texto, cor_fundo, cor_hover, fonte, imagem=None):
        self.rect = pygame.Rect(rect)
        self.texto = texto
        self.cor_fundo = cor_fundo
        self.cor_hover = cor_hover
        self.fonte = fonte
        self.imagem = imagem

    def desenhar(self, superficie):
        mouse_pos = pygame.mouse.get_pos()
        esta_hover = self.rect.collidepoint(mouse_pos)

        if self.imagem is not None:
            imagem = self.imagem
            if esta_hover:
                largura = int(self.imagem.get_width() * 1.05)
                altura = int(self.imagem.get_height() * 1.05)
                imagem = pygame.transform.smoothscale(self.imagem, (largura, altura))
            imagem_rect = imagem.get_rect(center=self.rect.center)
            self.rect.size = imagem_rect.size
            superficie.blit(imagem, imagem_rect)
        elif self.texto:
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


def carregar_e_recortar_imagens():
    base_dir = os.path.dirname(__file__)
    caminho_imagem = os.path.join(base_dir, "img", "pedra-papel-tesoura.jpg")

    sprite = pygame.image.load(caminho_imagem).convert_alpha()
    largura_total, altura = sprite.get_size()
    largura_icone = largura_total // 3

    pedra_surface = sprite.subsurface((0, 0, largura_icone, altura)).copy()
    papel_surface = sprite.subsurface((largura_icone, 0, largura_icone, altura)).copy()
    tesoura_surface = sprite.subsurface((2 * largura_icone, 0, largura_icone, altura)).copy()

    saida_dir = os.path.join(base_dir, "img")
    try:
        pygame.image.save(pedra_surface, os.path.join(saida_dir, "pedra.png"))
        pygame.image.save(papel_surface, os.path.join(saida_dir, "papel.png"))
        pygame.image.save(tesoura_surface, os.path.join(saida_dir, "tesoura.png"))
    except Exception:
        pass

    return pedra_surface, papel_surface, tesoura_surface


def main():
    pygame.init()
    pygame.display.set_caption("Pedra, Papel e Tesoura")
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    clock = pygame.time.Clock()

    fonte_titulo = pygame.font.SysFont("arial", 48, bold=True)
    fonte_texto = pygame.font.SysFont("arial", 28)
    fonte_pequena = pygame.font.SysFont("arial", 22)

    img_pedra, img_papel, img_tesoura = carregar_e_recortar_imagens()

    largura_botao = 180
    altura_botao = 70
    espacamento = 40
    y_botoes = ALTURA - 150

    total_largura = largura_botao * 3 + espacamento * 2
    inicio_x = (LARGURA - total_largura) // 2

    botoes = []
    cores = [AZUL, VERDE, VERMELHO]
    imagens_botoes_originais = [img_pedra, img_papel, img_tesoura]

    imagens_botoes = []
    altura_imagem = altura_botao - 20
    for img in imagens_botoes_originais:
        fator = altura_imagem / img.get_height()
        nova_largura = int(img.get_width() * fator)
        img_escalada = pygame.transform.smoothscale(img, (nova_largura, altura_imagem))
        imagens_botoes.append(img_escalada)

    for i, opcao in enumerate(OPCOES):
        x = inicio_x + i * (largura_botao + espacamento)
        botao = Botao(
            rect=(x, y_botoes, largura_botao, altura_botao),
            texto="",
            cor_fundo=cores[i],
            cor_hover=(min(cores[i][0] + 30, 255),
                       min(cores[i][1] + 30, 255),
                       min(cores[i][2] + 30, 255)),
            fonte=fonte_texto,
            imagem=imagens_botoes[i],
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
            texto_resultado = fonte_titulo.render(
                resultado,
                True,
                VERDE if resultado == "Você venceu!" else (
                    VERMELHO if resultado == "Computador venceu!" else CINZA_ESCURO
                ),
            )
            texto_placar_rodada = fonte_texto.render(
                f"Placar - Você: {placar_jogador}  Computador: {placar_computador}  Empates: {empates}",
                True,
                CINZA_ESCURO,
            )

            tela.blit(texto_jogador, (140, 240))
            tela.blit(texto_comp, (140, 290))

            resultado_rect = texto_resultado.get_rect(center=(LARGURA // 2, 360))
            tela.blit(texto_resultado, resultado_rect)

            placar_rodada_rect = texto_placar_rodada.get_rect(center=(LARGURA // 2, 400))
            tela.blit(texto_placar_rodada, placar_rodada_rect)

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

