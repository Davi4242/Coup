# Arquivo: src/player.py (VERSÃO CORRIGIDA FINAL)

import random
from typing import List, Dict, Type, Optional
from .action import Action, CoupAction, ForeignAidAction, IncomeAction

class Player:
    def __init__(self, name: str):
        self._name = name
        self._coins = 2
        self._characters: List[str] = []
        self._alive = True

    @property
    def name(self) -> str: return self._name
    @property
    def coins(self) -> int: return self._coins
    @coins.setter
    def coins(self, value: int) -> None: self._coins = max(0, value)
    @property
    def characters(self) -> List[str]: return self._characters
    @property
    def is_alive(self) -> bool: return self._alive

    def add_character(self, character: str) -> None:
        self._characters.append(character)

    def lose_influence(self) -> str:
        if not self.characters: return ""
        lost_card = ""
        if isinstance(self, HumanPlayer) and len(self.characters) > 1:
            print("\n" + "="*40)
            print("Terminal: Você precisa perder uma influência. Escolha qual carta revelar:")
            for i, card in enumerate(self.characters, 1):
                print(f"{i}. {card}")
            print("="*40)
            while True:
                try:
                    choice_str = input("Sua escolha (número): ")
                    if not choice_str: continue
                    choice = int(choice_str) - 1
                    if 0 <= choice < len(self.characters):
                        lost_card = self._characters.pop(choice)
                        break
                    else:
                        print("Escolha inválida.")
                except (ValueError, IndexError):
                    print("Por favor, insira um número válido.")
        else:
            lost_card = self._characters.pop(0)
        if not self.characters:
            self._alive = False
        return lost_card

    def reveal_character(self, character_name: str) -> Optional[Dict]:
        if character_name in self._characters:
            self._characters.remove(character_name)
            return {"character": character_name}
        return None

    def perform_action(self, action: Action, target=None, game_manager=None):
        if self.coins >= action.cost:
            self.coins -= action.cost
            return action.execute(self, target, game_manager)
        return f"{self.name} não tem moedas suficientes para {action.__class__.__name__}."

    def has_character(self, character_name: str) -> bool:
        return character_name in self._characters

    def choose_blocking_character(self, action: Action) -> Optional[str]:
        possible_blocks = [char for char in self.characters if char in action.blockable_by]
        if possible_blocks:
            return random.choice(possible_blocks)
        if action.blockable_by:
            return random.choice(action.blockable_by)
        return None

    def to_dict(self) -> Dict:
        return {"name": self.name, "coins": self.coins, "characters": self.characters, "alive": self.is_alive, "type": self.__class__.__name__}

    @classmethod
    def from_dict(cls, data: Dict[str, any]) -> 'Player':
        player_class_name = data.get("type", "AIPlayer")
        player_class = globals().get(player_class_name, AIPlayer)
        player = player_class(data.get("name", "Jogador"))
        player._coins = data.get("coins", 0)
        player._characters = data.get("characters", [])
        player._alive = data.get("alive", True)
        return player

    # Este método será sobrescrito nas classes filhas
    def wants_to_challenge(self, action_player: 'Player', action: Action) -> bool:
        return False

class HumanPlayer(Player):
    def wants_to_challenge(self, action_player: Player, action: Action) -> bool:
        print("\n" + "="*40)
        if action.requirement:
            print(f"Terminal: {action_player.name} está tentando usar a ação '{action.__class__.__name__}'.")
            print(f"Esta ação requer a influência '{action.requirement}'.")
            answer = input(f"{self.name}, você deseja DESAFIAR esta ação? (s/n): ").lower().strip()
        else:
            print(f"Terminal: {action_player.name} está tentando bloquear uma ação.")
            answer = input(f"{self.name}, você deseja DESAFIAR O BLOQUEIO? (s/n): ").lower().strip()
        print("="*40)
        return answer == 's'

    def wants_to_block(self, action: Action) -> bool:
        possible_blocks = [char for char in self.characters if char in action.blockable_by]
        block_options = action.blockable_by
        print("\n" + "="*40)
        print(f"Terminal: A ação '{action.__class__.__name__}' pode ser bloqueada por: {', '.join(block_options)}")
        if possible_blocks:
            print(f"Você tem: {', '.join(possible_blocks)}")
        else:
            print("Você não tem a carta para bloquear, mas pode blefar.")
        answer = input(f"{self.name}, você deseja BLOQUEAR esta ação? (s/n): ").lower().strip()
        print("="*40)
        return answer == 's'

class AIPlayer(Player):
    def wants_to_challenge(self, action_player: Player, action: Action) -> bool:
        if not action.requirement: # Não desafia bloqueios por enquanto, para simplificar
            return False
        if len(action_player.characters) == 1:
            return random.random() < 0.40
        return random.random() < 0.15

    def wants_to_block(self, action: Action) -> bool:
        if any(char in action.blockable_by for char in self.characters):
            return random.random() < 0.90
        return random.random() < 0.10

    def choose_action(self, available_actions: list, players: list) -> Optional[Action]:
        coup_action = next((a for a in available_actions if isinstance(a, CoupAction)), None)
        if coup_action and self.coins >= 10:
             return coup_action
        safe_actions = [a for a in available_actions if not a.requirement or self.has_character(a.requirement)]
        if safe_actions:
            priority_actions = [a for a in safe_actions if not isinstance(a, (IncomeAction, ForeignAidAction))]
            if priority_actions:
                return random.choice(priority_actions)
            return random.choice(safe_actions)
        actions_to_bluff = [a for a in available_actions if not isinstance(a, CoupAction)]
        if actions_to_bluff:
            return random.choice(actions_to_bluff)
        income_actions = [a for a in available_actions if isinstance(a, IncomeAction)]
        return income_actions[0] if income_actions else None