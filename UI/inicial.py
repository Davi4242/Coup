# Arquivo: UI/inicial.py (VERSÃO FINAL)

import pygame
from .setup import TELA, BRANCO, CINZA, PRETO, FONTE_TITULO, FONTE_GERAL

botao_iniciar_rect = pygame.Rect(300, 400, 200, 70)
botao_voltar_rect = pygame.Rect(300, 400, 200, 70) # Reutilizando a posição

def rodar_tela_inicial():
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            return "sair"  
        
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if botao_iniciar_rect.collidepoint(evento.pos):
                return "tela_login" 
            
    TELA.fill(BRANCO)
    texto_titulo = FONTE_TITULO.render("Coup", True, PRETO)
    TELA.blit(texto_titulo, (TELA.get_width()/2 - texto_titulo.get_width()/2, 150))
    
    pygame.draw.rect(TELA, CINZA, botao_iniciar_rect)
    texto_botao = FONTE_GERAL.render("Iniciar", True, PRETO)
    TELA.blit(texto_botao, (botao_iniciar_rect.centerx - texto_botao.get_width()/2, botao_iniciar_rect.centery - texto_botao.get_height()/2))

    return "tela_inicial"

def rodar_tela_game_over(game_manager):
    """
    Função para rodar a tela de Fim de Jogo.
    """
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            return "sair"
        
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if botao_voltar_rect.collidepoint(evento.pos):
                # Limpa os arquivos de estado para um novo jogo
                try:
                    os.remove("data/estado_jogo.json")
                    os.remove("data/deck_state.json")
                except OSError:
                    pass
                return "tela_inicial"

    TELA.fill(BRANCO)
    
    # Exibe a mensagem de Fim de Jogo
    texto_fim = FONTE_TITULO.render("Fim de Jogo", True, PRETO)
    TELA.blit(texto_fim, (TELA.get_width()/2 - texto_fim.get_width()/2, 150))
    
    # Exibe o vencedor (a última mensagem do histórico)
    if game_manager and game_manager.history:
        vencedor_texto = FONTE_GERAL.render(game_manager.history[-1], True, PRETO)
        TELA.blit(vencedor_texto, (TELA.get_width()/2 - vencedor_texto.get_width()/2, 250))
        
    # Botão para voltar ao início
    pygame.draw.rect(TELA, CINZA, botao_voltar_rect)
    texto_botao_voltar = FONTE_GERAL.render("Menu Inicial", True, PRETO)
    TELA.blit(texto_botao_voltar, (botao_voltar_rect.centerx - texto_botao_voltar.get_width()/2, botao_voltar_rect.centery - texto_botao_voltar.get_height()/2))
    
    return "tela_game_over"