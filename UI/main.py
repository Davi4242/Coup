import pygame
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.game_manager import GameManager
from src.player import HumanPlayer, AIPlayer
from .inicial import rodar_tela_inicial
from .login import rodar_tela_login, texto_usuario
from .jogo import rodar_tela_jogo
from . import setup

def main():
    estado_tela = "tela_inicial"
    menu_acoes_visivel = False
    game_manager = None
    relogio = pygame.time.Clock()
    rodando = True

    while rodando:
        # --- LÓGICA DE ESTADO DE TELA ---
        if estado_tela == "tela_inicial":
            estado_tela = rodar_tela_inicial()
        elif estado_tela == "tela_login":
            estado_tela = rodar_tela_login()
            if estado_tela == "tela_jogo":
                players = [HumanPlayer(texto_usuario or "Jogador"), AIPlayer("Bot 1"), AIPlayer("Bot 2"), AIPlayer("Bot 3")]
                game_manager = GameManager(players)
        elif estado_tela == "sair":
            rodando = False

        # --- LÓGICA DE TURNO E DESENHO ---
        if estado_tela == "tela_jogo" and game_manager:
            # ETAPA 1: SE FOR IA, DECLARA A AÇÃO
            if isinstance(game_manager.current_player, AIPlayer) and not game_manager.action_in_progress:
                game_manager.play_ai_turn()

            # ETAPA 2: A TELA É DESENHADA COM O ESTADO ATUAL
            estado_tela, menu_acoes_visivel = rodar_tela_jogo(game_manager, menu_acoes_visivel)
            pygame.display.flip()

            # ETAPA 3: SE UMA AÇÃO FOI DECLARADA, ELA É RESOLVIDA
            if game_manager.action_in_progress:
                pygame.time.wait(1500) # Pausa para ler a ação na tela
                game_manager.resolve_current_action()
        else:
            # Se não estamos na tela de jogo, apenas atualiza a tela
            pygame.display.flip()

        relogio.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()