import random
from .action import Action, IncomeAction, ForeignAidAction, CoupAction, TaxAction, AssassinateAction, StealAction, ExchangeAction, Challenge
from .player import Player, HumanPlayer, AIPlayer
from typing import List, Optional, Dict
import json
from pathlib import Path
from .Deck import Deck

class GameManager:
    def __init__(self, players: List[Player], state_file: str = "data/estado_jogo.json", load_existing: bool = False):
        self._players = players
        self._turn_index = 0
        self._history: List[str] = []
        self._deck = Deck()
        self._state_file = state_file
        self.action_in_progress: Optional[Dict] = None

        if load_existing and Path(self._state_file).exists():
            self.load_state()
        else:
            for p in self.players:
                p.coins = 2
                drawn = self._deck.draw(2)
                for card in drawn: p.add_character(card["character"])
            self.add_to_history(f"--- Jogo iniciado! Turno de {self.current_player.name} ---")
            self.save_state()

    MAPA_NOMES_ACOES = {
        "IncomeAction": "Renda", "ForeignAidAction": "Ajuda Externa", "CoupAction": "Golpe (Coup)",
        "TaxAction": "Taxar (Duque)", "AssassinateAction": "Assassinar", "StealAction": "Roubar (Capitão)",
        "ExchangeAction": "Trocar (Embaixador)"
    }

    @property
    def current_player(self) -> Player: return self._players[self._turn_index]
    @property
    def players(self) -> List[Player]: return self._players
    @property
    def history(self) -> List[str]: return self._history

    def get_available_actions(self, player: Player) -> List[Action]:
        actions = [IncomeAction(), ForeignAidAction(), TaxAction(), AssassinateAction(), StealAction(), ExchangeAction(), CoupAction()]
        if player.coins >= 10: return [CoupAction()]
        return [a for a in actions if player.coins >= a.cost]

    def add_to_history(self, message: str):
        if message: self._history.append(message)

    def next_turn(self):
        self.save_state()
        living_players = [p for p in self.players if p.is_alive]
        if len(living_players) <= 1:
            winner = living_players[0] if living_players else None
            if winner: self.add_to_history(f"Fim de Jogo! {winner.name} é o vencedor!")
            return True
        self._turn_index = (self._turn_index + 1) % len(self._players)
        while not self.current_player.is_alive:
            self._turn_index = (self._turn_index + 1) % len(self._players)
        self.add_to_history(f"--- Turno de {self.current_player.name} ---")
        return False

    def _declare_action(self, player: Player, action: Action):
        self.action_in_progress = {"player": player, "action": action, "target": None}
        action_name_friendly = self.MAPA_NOMES_ACOES.get(action.__class__.__name__, action.__class__.__name__)
        self.add_to_history(f"{player.name} usa a ação: {action_name_friendly}")
        
        if isinstance(action, (AssassinateAction, StealAction, CoupAction)):
            target = self._choose_target(player)
            if not target:
                self.add_to_history("Nenhum alvo válido. Turno perdido.")
                self.action_in_progress = None
                self.next_turn()
            else:
                self.add_to_history(f"...contra {target.name}.")
                self.action_in_progress["target"] = target
    
    def resolve_current_action(self):
        if not self.action_in_progress: return
        
        player = self.action_in_progress["player"]
        action = self.action_in_progress["action"]
        target = self.action_in_progress.get("target")
        
        if action.requirement:
            challenger = self._get_reactor(action, player, 'challenge', target)
            if challenger:
                self.add_to_history(f"!!! {challenger.name} desafia a ação!")
                challenge = Challenge(challenger, action, player)
                result, success = challenge.resolve(self)
                self.add_to_history(result)
                if success:
                    self.action_in_progress = None; self.next_turn(); return

        if action.blockable_by:
            blocker = self._get_reactor(action, player, 'block', target)
            if blocker:
                blocking_char = blocker.choose_blocking_character(action)
                self.add_to_history(f"### {blocker.name} bloqueia com {blocking_char}! ###")
                self.action_in_progress = None; self.next_turn(); return
        
        result = player.perform_action(action, target, self)
        self.add_to_history(result)
        self.action_in_progress = None
        self.next_turn()

    def execute_turn_from_ui(self, action_name: str):
        action_class_name = next((ac_name for ac_name, ac in self.MAPA_NOMES_ACOES.items() if ac == action_name), None)
        if action_class_name:
            action_obj = globals()[action_class_name]()
            self._declare_action(self.current_player, action_obj)
    
    def play_ai_turn(self):
        action = self.current_player.choose_action(self.get_available_actions(self.current_player), self.players)
        self._declare_action(self.current_player, action)

    def _get_reactor(self, action: Action, action_player: Player, reaction_type: str, target_player: Optional[Player] = None) -> Optional[Player]:
        potential_reactors = [p for p in self.players if p.is_alive and p is not action_player]
        
        if reaction_type == 'block' and target_player and target_player in potential_reactors:
            if target_player.wants_to_block(action, action_player): return target_player
        
        for reactor in potential_reactors:
            if reactor is target_player: continue
            if reaction_type == 'challenge' and reactor.wants_to_challenge(action_player, action): return reactor
            elif reaction_type == 'block' and reactor.wants_to_block(action, action_player): return reactor
        return None

    def _choose_target(self, current_player: Player) -> Optional[Player]:
        valid_targets = [p for p in self.players if p is not current_player and p.is_alive]
        if not valid_targets: return None
        if isinstance(current_player, HumanPlayer):
            print("\n" + "="*40); print("Terminal: Escolha um alvo para sua ação:")
            for i, target in enumerate(valid_targets, 1): print(f"{i}. {target.name} ({len(target.characters)} influências, {target.coins} moedas)")
            print("="*40)
            while True:
                try:
                    choice_str = input("Sua escolha (número): ");
                    if not choice_str: continue
                    choice = int(choice_str) - 1
                    if 0 <= choice < len(valid_targets): return valid_targets[choice]
                    else: print("Escolha inválida.")
                except ValueError: print("Entrada inválida. Por favor, insira um número.")
        else:
            human_players = [p for p in valid_targets if isinstance(p, HumanPlayer)]
            return random.choice(human_players) if human_players else random.choice(valid_targets)

    def save_state(self):
        data = {"turn_index": self._turn_index, "history": self._history, "players": [p.to_dict() for p in self._players], "deck_file": self._deck._json_file}
        Path(self._state_file).parent.mkdir(parents=True, exist_ok=True)
        with open(self._state_file, "w", encoding="utf-8") as f: json.dump(data, f, indent=2, ensure_ascii=False)

    def load_state(self):
        with open(self._state_file, "r", encoding="utf-8") as f: data = json.load(f)
        self._turn_index = data.get("turn_index", 0); self._history = data.get("history", [])
        self._deck = Deck(data.get("deck_file", "data/deck_state.json"))
        self._players = [Player.from_dict(pdata) for pdata in data.get("players", [])]