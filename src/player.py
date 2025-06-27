import random
from typing import List, Dict, Type
from .action import Action, CoupAction

class Player:
    def __init__(self, name: str):
        self._name = name
        self._coins = 0
        self._characters: List[str] = []
        self._alive = True
    
    @property
    def name(self) -> str: return self._name
    @property
    def coins(self) -> int: return self._coins
    @coins.setter
    def coins(self, value: int) -> None: self._coins = max(0, value)
    @property
    def characters(self) -> list: return self._characters
    @property
    def is_alive(self) -> bool: return self._alive

    def add_character(self, character: str) -> None:
        self._characters.append(character)
    
    def lose_influence(self) -> str:
        if not self.characters: return ""
        if isinstance(self, HumanPlayer) and len(self.characters) > 1:
            print("\n--- DECISÃO NO TERMINAL ---")
            print("Você precisa perder uma influência. Escolha qual carta revelar:")
            for i, card in enumerate(self.characters, 1): print(f"{i}. {card}")
            while True:
                try:
                    choice = int(input("Sua escolha: ")) - 1
                    if 0 <= choice < len(self.characters):
                        lost_card = self._characters.pop(choice)
                        break
                    else: print("Escolha inválida.")
                except (ValueError, IndexError): print("Por favor, insira um número válido.")
        else:
            lost_card = self._characters.pop(0)
        if not self.characters: self._alive = False
        return lost_card
    
    def perform_action(self, action: Action, target=None, game_manager=None):
        if self.coins >= action.cost:
            self.coins -= action.cost
            return action.execute(self, target, game_manager)
        return f"{self.name} não tem moedas suficientes."

    def has_character(self, character_name: str) -> bool:
        return character_name in self._characters

    def choose_blocking_character(self, action: Action) -> str:
        for character in self._characters:
            if character in action.blockable_by: return character
        return action.blockable_by[0] if action.blockable_by else ""

    def to_dict(self) -> Dict:
        return {"name": self.name, "coins": self.coins, "characters": self.characters, "alive": self.is_alive, "type": self.__class__.__name__}

    @classmethod
    def from_dict(cls, data: Dict[str, any]) -> 'Player':
        player_class = globals().get(data.get("type", "AIPlayer"), AIPlayer)
        player = player_class(data.get("name", "Jogador"))
        player._coins = data.get("coins", 0)
        player._characters = data.get("characters", [])
        player._alive = data.get("alive", True)
        return player

class HumanPlayer(Player):
    MAPA_NOMES_ACOES = {
        "IncomeAction": "Renda", "ForeignAidAction": "Ajuda Externa",
        "CoupAction": "Golpe (Coup)", "TaxAction": "Taxar (Duque)",
        "AssassinateAction": "Assassinar", "StealAction": "Roubar (Capitão)",
        "ExchangeAction": "Trocar (Embaixador)"
    }
    
    def wants_to_challenge(self, action_player: Player, action: Action) -> bool:
        action_name_friendly = self.MAPA_NOMES_ACOES.get(action.__class__.__name__, action.__class__.__name__)
        print("\n--- DECISÃO NO TERMINAL ---")
        answer = input(f"O jogador '{action_player.name}' usou a ação '{action_name_friendly}'.\nVocê ({self.name}), deseja desafiar? (s/n): ").lower().strip()
        return answer == 's'

    def wants_to_block(self, action: Action, action_player: Player) -> bool:
        if action.blockable_by:
            action_name_friendly = self.MAPA_NOMES_ACOES.get(action.__class__.__name__, action.__class__.__name__)
            print("\n--- DECISÃO NO TERMINAL ---")
            answer = input(f"A ação '{action_name_friendly}' de '{action_player.name}' pode ser bloqueada.\nVocê ({self.name}), deseja bloquear? (s/n): ").lower().strip()
            return answer == 's'
        return False

class AIPlayer(Player):
    def choose_action(self, available_actions: list, players: list) -> Action:
        if self.coins >= 10: return CoupAction()
        if self.coins >= 7: return CoupAction()
        safe_actions = [a for a in available_actions if not a.requirement or self.has_character(a.requirement)]
        return random.choice(safe_actions) if safe_actions else IncomeAction()

    def wants_to_challenge(self, action_player: Player, action: Action) -> bool:
        return random.random() < 0.20

    def wants_to_block(self, action: Action, action_player: Player) -> bool:
        if any(char in action.blockable_by for char in self.characters): return random.random() < 0.9
        return random.random() < 0.1