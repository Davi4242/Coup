from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, List, TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from .player import Player
    from .game_manager import GameManager

class Action(ABC):
    def __init__(self, cost: int, requirement: Optional[str] = None, blockable_by: Optional[List[str]] = None):
        self._cost = cost
        self._requirement = requirement
        self._blockable_by = blockable_by or []
    
    @property
    def cost(self) -> int: return self._cost
    @property
    def requirement(self) -> Optional[str]: return self._requirement
    @property
    def blockable_by(self) -> List[str]: return self._blockable_by
    
    @abstractmethod
    def execute(self, attacker: 'Player', target: Optional['Player'], game_manager: 'GameManager') -> str:
        pass

class IncomeAction(Action):
    def __init__(self): super().__init__(cost=0)
    def execute(self, attacker: 'Player', target: Optional['Player'], game_manager: 'GameManager') -> str:
        attacker.coins += 1
        return f"{attacker.name} pegou Renda (+1 moeda)."

class ForeignAidAction(Action):
    def __init__(self): super().__init__(cost=0, blockable_by=["Duque"])
    def execute(self, attacker: 'Player', target: Optional['Player'], game_manager: 'GameManager') -> str:
        attacker.coins += 2
        return f"{attacker.name} pegou Ajuda Externa (+2 moedas)."

class CoupAction(Action):
    def __init__(self): super().__init__(cost=7)
    def execute(self, attacker: 'Player', target: Optional['Player'], game_manager: 'GameManager') -> str:
        if not target: return f"{attacker.name} tentou dar um Golpe, mas não havia alvo."
        lost_card = target.lose_influence()
        game_manager._deck.discard({"character": lost_card})
        return f"{attacker.name} deu um Golpe em {target.name}! Perdeu '{lost_card}'."

class TaxAction(Action):
    def __init__(self): super().__init__(cost=0, requirement="Duque")
    def execute(self, attacker: 'Player', target: Optional['Player'], game_manager: 'GameManager') -> str:
        attacker.coins += 3
        return f"{attacker.name} coletou Impostos (+3 moedas)."

class AssassinateAction(Action):
    def __init__(self): super().__init__(cost=3, requirement="Assassino", blockable_by=["Condessa"])
    def execute(self, attacker: 'Player', target: Optional['Player'], game_manager: 'GameManager') -> str:
        if not target: return f"{attacker.name} tentou assassinar, mas não havia alvo."
        lost_card = target.lose_influence()
        game_manager._deck.discard({"character": lost_card})
        return f"{attacker.name} assassinou {target.name}! Perdeu '{lost_card}'."

class StealAction(Action):
    def __init__(self): super().__init__(cost=0, requirement="Capitao", blockable_by=["Capitao", "Embaixador"])
    def execute(self, attacker: 'Player', target: Optional['Player'], game_manager: 'GameManager') -> str:
        if not target: return f"{attacker.name} tentou roubar, mas não havia alvo."
        stolen_amount = min(2, target.coins)
        target.coins -= stolen_amount
        attacker.coins += stolen_amount
        return f"{attacker.name} roubou {stolen_amount} moedas de {target.name}."

class ExchangeAction(Action):
    def __init__(self): super().__init__(cost=0, requirement="Embaixador")
    def execute(self, attacker: 'Player', target: Optional['Player'], game_manager: 'GameManager') -> str:
        return f"{attacker.name} usou o Embaixador para trocar cartas."

class Challenge:
    def __init__(self, challenger: 'Player', action: Action, action_player: 'Player'):
        self.challenger = challenger
        self.action = action
        self.action_player = action_player
    
    def resolve(self, game_manager: 'GameManager') -> Tuple[str, bool]:
        player_being_challenged = self.action_player
        required_character = self.action.requirement
        has_character = player_being_challenged.has_character(required_character)
        
        if has_character:
            # Desafio Falhou: desafiante perde vida, desafiado troca a carta.
            lost_card = self.challenger.lose_influence()
            game_manager.add_to_history(f"{player_being_challenged.name} provou ter {required_character} e troca de carta.")
            # Lógica simples de troca: devolve a carta e pega uma nova
            player_being_challenged.characters.remove(required_character)
            game_manager._deck.return_cards([{"character": required_character}])
            new_cards = game_manager._deck.draw(1)
            if new_cards: player_being_challenged.add_character(new_cards[0]['character'])
            
            message = f"Desafio falhou! {self.challenger.name} perdeu '{lost_card}'."
            return message, False
        else:
            # Desafio Bem-sucedido: desafiado perde a vida.
            lost_card = player_being_challenged.lose_influence()
            message = f"Desafio teve sucesso! {player_being_challenged.name} não tinha '{required_character}' e perdeu '{lost_card}'."
            return message, True

class Block:
    def __init__(self, blocker: 'Player', action: Action, blocking_character: str):
        self.blocker = blocker; self.action = action; self.blocking_character = blocking_character
    def resolve(self, game: 'GameManager') -> str:
        return f"Ação bloqueada por {self.blocker.name} com {self.blocking_character}."