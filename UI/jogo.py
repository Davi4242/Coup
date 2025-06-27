# Arquivo: UI/jogo.py (VERSÃO CORRIGIDA)

import pygame
import os
import sys
from typing import Dict, List

from .setup import *

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.game_manager import GameManager
from src.player import HumanPlayer

def montar_estado(game_manager: GameManager) -> dict:
    """Converte o objeto GameManager em um dicionário simples para a UI usar."""
    players = game_manager.players
    descartadas = [c.get("character") for c in game_manager._deck._discard_pile] if hasattr(game_manager, "_deck") else []
    
    def info_oponente(idx: int) -> dict:
        if idx < len(players):
            p = players[idx]
            return {"nome": p.name, "moedas": p.coins if p.is_alive else "-", "cartas": len(p.characters), "vivo": p.is_alive}
        return {"nome": "", "moedas": "-", "cartas": 0, "vivo": False}

    return {
        "turno_de": game_manager.current_player.name,
        # CORREÇÃO: Pega os últimos 3 eventos para exibir na tela
        "log_eventos": game_manager.history[-3:],
        "cartas_reveladas": descartadas,
        "jogador": {"nome": players[0].name, "moedas": players[0].coins, "cartas": [c for c in players[0].characters]},
        "oponentes": {"esquerda": info_oponente(1), "topo": info_oponente(2), "direita": info_oponente(3)},
    }

# --- DEFINIÇÕES DE ELEMENTOS DA INTERFACE ---
# Aumentado para caber 3 linhas de texto
info_rect = pygame.Rect(0, 0, 700, 80)
info_rect.center = (TELA_RECT.centerx, TELA_RECT.centery)
FONTE_ACAO = pygame.font.Font(None, 22) # Fonte um pouco menor para caber
LARGURA_CARTA_JOGADOR, ALTURA_CARTA_JOGADOR = int(LARGURA_CARTA*1.2), int(ALTURA_CARTA*1.2)
ESPACAMENTO_JOGADOR = int(ESPACAMENTO_CARTAS * 0.2)
CARTAS_JOGADOR_GRANDES = {nome: pygame.transform.scale(img, (LARGURA_CARTA_JOGADOR, ALTURA_CARTA_JOGADOR)) for nome, img in CARTAS_FRENTE_IMGS.items()}
botao_acao_rect = pygame.Rect(0, 0, 150, 60)
botao_acao_rect.bottomright = (TELA_RECT.right - MARGEM, TELA_RECT.bottom - MARGEM)
fundo_menu_rect = pygame.Rect(0, 0, 400, 500)
fundo_menu_rect.center = TELA_RECT.center

# --- FUNÇÕES DE DESENHO ---
def desenhar_info_jogador(pos_texto, nome, moedas, cor_texto=PRETO):
    texto_nome = FONTE_GERAL.render(nome, True, cor_texto)
    texto_moedas = FONTE_GERAL.render(f"$ {moedas}", True, cor_texto)
    TELA.blit(texto_nome, texto_nome.get_rect(center=(pos_texto[0], pos_texto[1] - 20)))
    TELA.blit(texto_moedas, texto_moedas.get_rect(center=(pos_texto[0], pos_texto[1] + 20)))

def desenhar_cartas_jogador(pos_base: tuple, lista_cartas: list):
    if not lista_cartas: return
    # Os nomes de personagem no GameManager são "Duque", "Assassino", etc.
    # As chaves em CARTAS_JOGADOR_GRANDES são "duque", "assassino", etc.
    # Precisamos converter para minúsculo.
    nomes_formatados = [nome.lower() for nome in lista_cartas]
    
    largura_total = (len(nomes_formatados) * LARGURA_CARTA_JOGADOR) + ((len(nomes_formatados) - 1) * ESPACAMENTO_JOGADOR)
    start_x = pos_base[0] - largura_total / 2
    for i, nome_carta in enumerate(nomes_formatados):
        imagem_carta = CARTAS_JOGADOR_GRANDES.get(nome_carta)
        if imagem_carta:
            pos_x = start_x + i * (LARGURA_CARTA_JOGADOR + ESPACAMENTO_JOGADOR)
            pos_y = pos_base[1] - ALTURA_CARTA_JOGADOR - MARGEM
            TELA.blit(imagem_carta, (pos_x, pos_y))

def desenhar_cartas_oponente(pos_base: tuple, qtd_cartas: int, angulo: int):
    if qtd_cartas <= 0: return
    carta_rotacionada = pygame.transform.rotate(CARTA_VERSO_IMG, angulo)
    rect_rotacionado = carta_rotacionada.get_rect()
    if angulo == 180:
        largura_total = (qtd_cartas * LARGURA_CARTA) + ((qtd_cartas - 1) * ESPACAMENTO_CARTAS)
        start_x = pos_base[0] - largura_total / 2
        for i in range(qtd_cartas):
            pos_x = start_x + i * (LARGURA_CARTA + ESPACAMENTO_CARTAS)
            TELA.blit(carta_rotacionada, (pos_x, pos_base[1] + MARGEM))
    elif angulo == 90:
        altura_total = (qtd_cartas * LARGURA_CARTA) + ((qtd_cartas - 1) * ESPACAMENTO_CARTAS)
        start_y = pos_base[1] - altura_total / 2
        for i in range(qtd_cartas):
            pos_y = start_y + i * (LARGURA_CARTA + ESPACAMENTO_CARTAS)
            rect_rotacionado.topleft = (pos_base[0] + MARGEM, pos_y)
            TELA.blit(carta_rotacionada, rect_rotacionado)
    elif angulo == 270:
        altura_total = (qtd_cartas * LARGURA_CARTA) + ((qtd_cartas - 1) * ESPACAMENTO_CARTAS)
        start_y = pos_base[1] - altura_total / 2
        for i in range(qtd_cartas):
            pos_y = start_y + i * (LARGURA_CARTA + ESPACAMENTO_CARTAS)
            rect_rotacionado.topright = (pos_base[0] - MARGEM, pos_y)
            TELA.blit(carta_rotacionada, rect_rotacionado)

def desenhar_cartas_reveladas(lista_cartas: list):
    if not lista_cartas: return
    start_x, pos_y = MARGEM, MARGEM * 3
    espacamento_reveladas = LARGURA_CARTA_REVELADA * 0.4
    for i, nome_carta in enumerate(lista_cartas):
        imagem = CARTAS_REVELADAS_IMGS.get(nome_carta.lower())
        if imagem:
            TELA.blit(imagem, (start_x + i * espacamento_reveladas, pos_y))

def desenhar_menu_de_acoes(botoes_do_menu: Dict[str, pygame.Rect]):
    fundo_transparente = pygame.Surface(TELA.get_size(), pygame.SRCALPHA); fundo_transparente.fill((0,0,0,180)); TELA.blit(fundo_transparente, (0,0))
    pygame.draw.rect(TELA, BRANCO, fundo_menu_rect); pygame.draw.rect(TELA, PRETO, fundo_menu_rect, 2)
    texto_titulo = FONTE_TITULO.render("Escolha uma Ação", True, PRETO); rect_titulo = texto_titulo.get_rect(center=(fundo_menu_rect.centerx, fundo_menu_rect.y + 40)); TELA.blit(texto_titulo, rect_titulo)
    for nome_acao, rect_acao in botoes_do_menu.items():
        pygame.draw.rect(TELA, CINZA, rect_acao); texto_acao = FONTE_GERAL.render(nome_acao, True, PRETO); rect_texto_acao = texto_acao.get_rect(center=rect_acao.center); TELA.blit(texto_acao, rect_texto_acao)

def desenhar_log_eventos(rect: pygame.Rect, log: List[str]):
    """Desenha as últimas mensagens do histórico dentro do retângulo fornecido."""
    pygame.draw.rect(TELA, (240, 240, 240), rect)
    pygame.draw.rect(TELA, PRETO, rect, 2)
    
    altura_linha = FONTE_ACAO.get_height()
    # Desenha as linhas de baixo para cima
    for i, texto_str in enumerate(reversed(log)):
        texto_surf = FONTE_ACAO.render(texto_str, True, PRETO)
        pos_y = rect.bottom - (i + 1) * altura_linha - 5 # 5 pixels de margem inferior
        texto_rect = texto_surf.get_rect(centerx=rect.centerx, y=pos_y)
        TELA.blit(texto_surf, texto_rect)

# --- FUNÇÃO PRINCIPAL DO MÓDULO ---
def rodar_tela_jogo(game_manager: GameManager, menu_visivel_atual: bool):
    menu_acoes_visivel = menu_visivel_atual
    botoes_do_menu = {}
    
    jogador_humano_no_turno = isinstance(game_manager.current_player, HumanPlayer)

    if menu_acoes_visivel and jogador_humano_no_turno:
        acoes = game_manager.get_available_actions(game_manager.current_player)
        mapa_nomes = {"IncomeAction": "Renda", "ForeignAidAction": "Ajuda Externa", "CoupAction": "Golpear (Coup)", "TaxAction": "Taxar (Duque)", "AssassinateAction": "Assassinar", "StealAction": "Roubar (Capitão)", "ExchangeAction": "Trocar (Embaixador)"}
        start_y, espaco = fundo_menu_rect.y + 100, 65
        for i, acao in enumerate(acoes):
            nome = mapa_nomes.get(acao.__class__.__name__, acao.__class__.__name__)
            rect = pygame.Rect(0, 0, 300, 50); rect.center = (fundo_menu_rect.centerx, start_y + i * espaco); botoes_do_menu[nome] = rect

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT: return "sair", menu_acoes_visivel
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if menu_acoes_visivel and jogador_humano_no_turno:
                nome_acao_clicada = next((nome for nome, rect in botoes_do_menu.items() if rect.collidepoint(evento.pos)), None)
                if nome_acao_clicada:
                    game_manager.execute_turn_from_ui(nome_acao_clicada)
                    menu_acoes_visivel = False
                elif not fundo_menu_rect.collidepoint(evento.pos):
                    menu_acoes_visivel = False
            elif botao_acao_rect.collidepoint(evento.pos) and jogador_humano_no_turno:
                menu_acoes_visivel = True

    estado = montar_estado(game_manager)
    TELA.fill(BRANCO)
    
    TELA.blit(FONTE_GERAL.render(f"Turno de: {estado['turno_de']}", True, PRETO), (MARGEM, MARGEM))
    
    jogador_info = estado['jogador']
    desenhar_cartas_jogador((TELA_RECT.centerx, TELA_RECT.bottom), jogador_info['cartas'])
    desenhar_info_jogador((TELA_RECT.centerx, TELA_RECT.bottom - ALTURA_CARTA_JOGADOR - 50), jogador_info['nome'], jogador_info['moedas'])
    
    for pos, op_info in [('esquerda', estado['oponentes']['esquerda']), ('direita', estado['oponentes']['direita']), ('topo', estado['oponentes']['topo'])]:
        if op_info['vivo']:
            if pos == 'esquerda':
                pos_base = (TELA_RECT.left, TELA_RECT.centery); angulo = 90
                pos_texto_moedas = (pos_base[0] + ALTURA_CARTA/2 + MARGEM, pos_base[1])
            elif pos == 'direita':
                pos_base = (TELA_RECT.right, TELA_RECT.centery); angulo = 270
                pos_texto_moedas = (pos_base[0] - ALTURA_CARTA/2 - MARGEM, pos_base[1])
            else:
                pos_base = (TELA_RECT.centerx, TELA_RECT.top); angulo = 180
                pos_texto_moedas = (pos_base[0], pos_base[1] + ALTURA_CARTA + 40)
            desenhar_cartas_oponente(pos_base, op_info['cartas'], angulo)
            desenhar_info_jogador(pos_texto_moedas, op_info['nome'], op_info['moedas'])
    
    desenhar_cartas_reveladas(estado['cartas_reveladas'])
    
    # CORREÇÃO: Chama a nova função para desenhar o log de eventos
    desenhar_log_eventos(info_rect, estado['log_eventos'])
    
    if menu_acoes_visivel and jogador_humano_no_turno:
        desenhar_menu_de_acoes(botoes_do_menu)
    
    if jogador_humano_no_turno:
        pygame.draw.rect(TELA, CINZA, botao_acao_rect)
        texto_botao = FONTE_GERAL.render("Ação", True, PRETO)
        TELA.blit(texto_botao, texto_botao.get_rect(center=botao_acao_rect.center))
    
    return "tela_jogo", menu_acoes_visivel