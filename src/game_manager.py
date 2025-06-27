# Arquivo: src/game_manager.py (VERSÃO COM NOMES AMIGÁVEIS)

import random
from .action import Action, IncomeAction, ForeignAidAction, CoupAction, TaxAction, AssassinateAction, StealAction, ExchangeAction, Challenge, Block
from .player import Player, HumanPlayer, AIPlayer
from typing import List, Optional
import json
from pathlib import Path
from .Deck import Deck

# MAPA DE NOMES AMIGÁVEIS PARA AS AÇÕES
ACTION_PRETTY_NAMES = {
    "IncomeAction": "Renda",
    "ForeignAidAction": "Ajuda Externa",
    "CoupAction": "Golpe de Estado",
    "TaxAction": "Taxar (Duque)",
    "AssassinateAction": "Assassinar",
    "StealAction": "Roubar (Capitão)",
    "ExchangeAction": "Trocar (Embaixador)"
}

class GameManager:
    def __init__(self, players: List[Player], state_file: str = "data/estado_jogo.json", load_existing: bool = False):
        self._players = players
        self._turn_index = 0
        self._history: List[str] = []
        self._deck = Deck()
        self._state_file = state_file

        if load_existing and Path(self._state_file).exists():
            self.load_state()
        else:
            for p in self.players:
                p.coins = 2
                drawn = self._deck.draw(2)
                for card in drawn:
                    p.add_character(card["character"])
            self.add_to_history("--- Jogo iniciado! ---")
            self.save_state()

    @property
    def current_player(self) -> Player:
        return self._players[self._turn_index]

    @property
    def players(self) -> List[Player]:
        return self._players

    @property
    def history(self) -> List[str]:
        return self._history

    def get_available_actions(self, player: Player) -> List[Action]:
        actions = [IncomeAction(), ForeignAidAction(), TaxAction(), AssassinateAction(), StealAction(), ExchangeAction(), CoupAction()]
        return [a for a in actions if player.coins >= a.cost]

    def add_to_history(self, message: str):
        if message:
            self._history.append(message)

    def next_turn(self):
        self.save_state()
        if len([p for p in self.players if p.is_alive]) <= 1:
            winner = next((p for p in self.players if p.is_alive), None)
            if winner:
                self.add_to_history(f"Fim de Jogo! {winner.name} é o vencedor!")
            return

        self._turn_index = (self._turn_index + 1) % len(self._players)
        while not self.current_player.is_alive:
            self._turn_index = (self._turn_index + 1) % len(self._players)
        self.add_to_history(f"--- Turno de {self.current_player.name} ---")

    def _get_reactor(self, action: Action, action_player: Player, reaction_type: str, target_player: Optional[Player] = None) -> Optional[Player]:
        potential_reactors = [p for p in self.players if p.is_alive and p is not action_player]
        human_player = next((p for p in potential_reactors if isinstance(p, HumanPlayer)), None)
        if human_player:
            if reaction_type == 'challenge' and action.requirement and human_player.wants_to_challenge(action_player, action):
                return human_player
            elif reaction_type == 'block' and (isinstance(action, ForeignAidAction) or human_player is target_player) and human_player.wants_to_block(action):
                return human_player

        for bot in [p for p in potential_reactors if isinstance(p, AIPlayer)]:
            if reaction_type == 'challenge' and action.requirement and bot.wants_to_challenge(action_player, action):
                return bot
            elif reaction_type == 'block' and (isinstance(action, ForeignAidAction) or bot is target_player) and bot.wants_to_block(action):
                return bot
        return None

    def _run_full_turn_logic(self, player: Player, action: Action):
        action_name = ACTION_PRETTY_NAMES.get(action.__class__.__name__, action.__class__.__name__)
        self.add_to_history(f"{player.name} tenta usar {action_name}")
        
        target = None
        if isinstance(action, (AssassinateAction, StealAction, CoupAction)):
            target = self._choose_target(player)
            if not target:
                self.add_to_history(f"Ação cancelada (sem alvo).")
                self.next_turn()
                return
            self.add_to_history(f"...alvo: {target.name}.")

        if action.requirement:
            challenger = self._get_reactor(action, player, 'challenge')
            if challenger:
                self.add_to_history(f"!!! {challenger.name} desafia!")
                challenge = Challenge(challenger, action, player)
                result_message, challenge_successful = challenge.resolve(self)
                self.add_to_history(result_message)
                if challenge_successful:
                    self.next_turn()
                    return

        if action.blockable_by:
            blocker = self._get_reactor(action, player, 'block', target)
            if blocker:
                blocking_char = blocker.choose_blocking_character(action)
                if blocking_char:
                    self.add_to_history(f"### {blocker.name} bloqueia com {blocking_char}!")
                    if player.wants_to_challenge(blocker, action):
                        self.add_to_history(f"!!! {player.name} desafia o bloqueio!")
                        if blocker.has_character(blocking_char):
                            self.add_to_history(f"Bloqueio confirmado. Ação cancelada.")
                            player.lose_influence()
                        else:
                            self.add_to_history(f"Bloqueio era blefe! Ação continua.")
                            blocker.lose_influence()
                            result = player.perform_action(action, target, self)
                            self.add_to_history(result)
                    else:
                        self.add_to_history("Bloqueio aceito. Ação cancelada.")
                self.next_turn()
                return

        result = player.perform_action(action, target, self)
        self.add_to_history(result)
        self.next_turn()

    def execute_turn_from_ui(self, action_name: str):
        mapa_nomes_invertido = {v: k for k, v in ACTION_PRETTY_NAMES.items()}
        action_class_name = mapa_nomes_invertido.get(action_name)

        action_classes = {
            "IncomeAction": IncomeAction, "ForeignAidAction": ForeignAidAction, "CoupAction": CoupAction,
            "TaxAction": TaxAction, "AssassinateAction": AssassinateAction, "StealAction": StealAction,
            "ExchangeAction": ExchangeAction
        }
        action_class = action_classes.get(action_class_name)
        
        if action_class:
            self._run_full_turn_logic(self.current_player, action_class())

    def play_ai_turn(self):
        player = self.current_player
        available_actions = self.get_available_actions(player)
        action = player.choose_action(available_actions, self.players)
        if action:
            self._run_full_turn_logic(player, action)
        else:
            self.add_to_history(f"{player.name} passou o turno.")
            self.next_turn()

    def _choose_target(self, current_player: Player) -> Optional[Player]:
        valid_targets = [p for p in self.players if p is not current_player and p.is_alive]
        if not valid_targets: return None
        if isinstance(current_player, HumanPlayer):
            print("\n" + "=" * 40)
            print("Terminal: Escolha um alvo para sua ação:")
            for i, target in enumerate(valid_targets, 1):
                print(f"{i}. {target.name} ({len(target.characters)} influências, {target.coins} moedas)")
            print("=" * 40)
            while True:
                try:
                    choice_str = input("Sua escolha (número): ")
                    if not choice_str: continue
                    choice = int(choice_str) - 1
                    if 0 <= choice < len(valid_targets):
                        return valid_targets[choice]
                    else:
                        print("Escolha inválida. Tente novamente.")
                except ValueError:
                    print("Entrada inválida. Por favor, insira um número.")
        else:
            human_players = [p for p in valid_targets if isinstance(p, HumanPlayer)]
            return random.choice(human_players) if human_players else random.choice(valid_targets)

    def save_state(self):
        data = {"turn_index": self._turn_index, "history": self._history, "players": [p.to_dict() for p in self._players], "deck_file": self._deck._json_file}
        Path(self._state_file).parent.mkdir(parents=True, exist_ok=True)
        with open(self._state_file, "w", encoding="utf-8") as f: json.dump(data, f, indent=2, ensure_ascii=False)

    def load_state(self):
        with open(self._state_file, "r", encoding="utf-8") as f: data = json.load(f)
        self._turn_index = data.get("turn_index", 0)
        self._history = data.get("history", [])
        self._deck = Deck(data.get("deck_file", "data/deck_state.json"))
        self._players = [Player.from_dict(pdata) for pdata in data.get("players", [])]