# Arquivo: UI/main.py (VERSÃO FINAL)

import pygame
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.game_manager import GameManager
from src.player import HumanPlayer, AIPlayer
# CORREÇÃO: Importa a nova tela de game over
from .inicial import rodar_tela_inicial, rodar_tela_game_over
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
        # CORREÇÃO: Lógica para verificar o fim de jogo
        if estado_tela == "tela_jogo" and game_manager:
            jogadores_vivos = [p for p in game_manager.players if p.is_alive]
            jogador_humano = game_manager.players[0]
            
            # Se o jogador humano foi eliminado ou se só resta um jogador
            if not jogador_humano.is_alive or len(jogadores_vivos) <= 1:
                # Adiciona a mensagem de vitória se ainda não houver
                if len(jogadores_vivos) == 1 and "vencedor" not in game_manager.history[-1]:
                     game_manager.add_to_history(f"Fim de Jogo! {jogadores_vivos[0].name} é o vencedor!")
                elif not jogador_humano.is_alive and "vencedor" not in game_manager.history[-1]:
                    # Procura um vencedor entre os bots
                    if len(jogadores_vivos) == 1:
                         game_manager.add_to_history(f"Fim de Jogo! {jogadores_vivos[0].name} é o vencedor!")
                    else: # Caso raro de empate ou múltiplos vencedores
                         game_manager.add_to_history("Você foi eliminado! Fim de Jogo.")
                
                estado_tela = "tela_game_over"

        if estado_tela == "tela_inicial":
            estado_tela = rodar_tela_inicial()
        elif estado_tela == "tela_login":
            estado_tela = rodar_tela_login()
            if estado_tela == "tela_jogo":
                # Reseta o game_manager para um novo jogo
                players = [HumanPlayer(texto_usuario or "Humano"), AIPlayer("Bot 1"), AIPlayer("Bot 2"), AIPlayer("Bot 3")]
                game_manager = GameManager(players)
        elif estado_tela == "tela_game_over":
            estado_tela = rodar_tela_game_over(game_manager)
            if estado_tela == "tela_inicial":
                game_manager = None # Garante que o jogo será recriado
        elif estado_tela == "sair":
            rodando = False

        if estado_tela == "tela_jogo" and game_manager:
            current_player = game_manager.current_player
            
            if isinstance(current_player, AIPlayer):
                game_manager.play_ai_turn()

            estado_tela, menu_acoes_visivel = rodar_tela_jogo(game_manager, menu_acoes_visivel)

            if isinstance(current_player, AIPlayer):
                pygame.display.flip()
                pygame.time.wait(1500) # Pausa um pouco menor
                continue 

        pygame.display.flip()
        relogio.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()