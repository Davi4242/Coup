

# Coup Game

Este projeto implementa uma versão simplificada do jogo de blefe **Coup** em Python  para o trabalho da disciplina Programação Orientada a Objetos de Davi Lessa, Marcella Almeida e Murilo Paulo.

## Requisitos

- Python 3.8 ou superior
- [pygame](https://www.pygame.org/)

Instale o pygame com:

```bash
pip install pygame
```

## Como jogar

Execute o arquivo principal do jogo:

```bash
python -m UI.main
```

Você precisará de uma janela gráfica para jogar e algumas interações com o terminal. O jogo cria quatro participantes: um jogador humano e três oponentes controlados pela IA.

## Organização do código

- `src/action.py` – define as ações, desafios e bloqueios.
- `src/game_manager.py` – gerencia turnos e persistência do estado.
- `src/player.py` – classes de jogadores humanos e IA.
- `UI/` – interface gráfica construída com pygame.
- `data/` – arquivos de estado salvos (baralho e jogo).

Bom jogo!


