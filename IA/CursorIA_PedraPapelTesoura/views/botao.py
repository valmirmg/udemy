import pygame

from .constants import PRETO


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
            superficie.blit(imagem, imagem_rect)
        elif self.texto:
            texto_render = self.fonte.render(self.texto, True, PRETO)
            texto_rect = texto_render.get_rect(center=self.rect.center)
            superficie.blit(texto_render, texto_rect)

    def foi_clicado(self, evento) -> bool:
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect.collidepoint(evento.pos):
                return True
        return False

