# Arquivo: src/action.py (VERSÃO CORRIGIDA)

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
    def blockable_by(self) -> List[str]:
        return self._blockable_by
    
    @property
    def cost(self) -> int:
        return self._cost
    
    @property
    def requirement(self) -> Optional[str]:
        return self._requirement
    
    @abstractmethod
    def execute(
        self,
        attacker: 'Player',
        target: Optional['Player'] = None,
        game_manager: Optional['GameManager'] = None,
    ) -> str:
        pass

class IncomeAction(Action):
    def __init__(self):
        super().__init__(cost=0)

    def execute(self, attacker: 'Player', target: Optional['Player'] = None, game_manager: Optional['GameManager'] = None) -> str:
        attacker.coins += 1
        return f"Ação: {attacker.name} pegou Renda (+1 moeda)."

class ForeignAidAction(Action):
    def __init__(self):
        super().__init__(cost=0, blockable_by=["Duque"])

    def execute(self, attacker: 'Player', target: Optional['Player'] = None, game_manager: Optional['GameManager'] = None) -> str:
        attacker.coins += 2
        return f"Ação: {attacker.name} pegou Ajuda Externa (+2 moedas)."

class CoupAction(Action):
    def __init__(self):
        super().__init__(cost=7)
    
    def execute(self, attacker: 'Player', target: Optional['Player'], game_manager: Optional['GameManager'] = None) -> str:
        if not target: raise ValueError("CoupAction requer um alvo.")
        if not target.is_alive: return f"{target.name} já está eliminado."
        
        lost_card = target.lose_influence()
        return f"Ação: {attacker.name} deu um Golpe em {target.name}, que perdeu '{lost_card}'."

class TaxAction(Action):
    def __init__(self):
        super().__init__(cost=0, requirement="Duque")
    
    def execute(self, attacker: 'Player', target: Optional['Player'] = None, game_manager: Optional['GameManager'] = None) -> str:
        attacker.coins += 3
        return f"Ação: {attacker.name} usou o Duque para taxar (+3 moedas)."

class AssassinateAction(Action):
    def __init__(self):
        super().__init__(cost=3, requirement="Assassino", blockable_by=["Condessa"])
    
    def execute(self, attacker: 'Player', target: Optional['Player'] = None, game_manager: Optional['GameManager'] = None) -> str:
        if not target: raise ValueError("Assassinar precisa de um alvo.")
        if not target.is_alive: return f"{target.name} já está eliminado."
        
        lost_card = target.lose_influence()
        return f"Ação: {attacker.name} assassinou {target.name}, que perdeu '{lost_card}'."

class StealAction(Action):
    def __init__(self):
        super().__init__(cost=0, requirement="Capitao", blockable_by=["Capitao", "Embaixador"])
    
    def execute(self, attacker: 'Player', target: Optional['Player'] = None, game_manager: Optional['GameManager'] = None) -> str:
        if not target: raise ValueError("Roubo precisa de um alvo.")
        
        stolen_amount = min(2, target.coins)
        target.coins -= stolen_amount
        attacker.coins += stolen_amount
        
        return f"Ação: {attacker.name} roubou {stolen_amount} moedas de {target.name}."

class ExchangeAction(Action):
    def __init__(self):
        super().__init__(cost=0, requirement="Embaixador")
    
    def execute(self, attacker: 'Player', target: Optional['Player'] = None, game_manager: Optional['GameManager'] = None) -> str:
        return f"{attacker.name} usou o Embaixador (não implementado)."

class Challenge:
    def __init__(self, challenger: 'Player', action: Action, action_player: 'Player'):
        self._challenger = challenger
        self._action = action
        self._action_player = action_player
    
    def resolve(self, game_manager: 'GameManager') -> Tuple[str, bool]:
        player_being_challenged = self._action_player
        required_character = self._action.requirement
        
        has_character = player_being_challenged.has_character(required_character)
        
        if has_character:
            lost_influence_on_challenge = self._challenger.lose_influence()
            message = (f"Desafio falhou! {player_being_challenged.name} provou ter '{required_character}'. "
                       f"{self._challenger.name} perdeu '{lost_influence_on_challenge}'.")
            
            # Lógica de troca de carta
            if game_manager and game_manager._deck:
                 revealed_card_info = player_being_challenged.reveal_character(required_character)
                 if revealed_card_info:
                    drawn_cards = game_manager._deck.draw(1)
                    # CORREÇÃO: Se o baralho acabar, devolve a carta ao jogador
                    if not drawn_cards:
                        player_being_challenged.add_character(revealed_card_info['character'])
                        message += " (O baralho está vazio, a carta foi devolvida)."
                    else:
                        game_manager._deck.return_cards([revealed_card_info])
                        player_being_challenged.add_character(drawn_cards[0]['character'])

            return message, False
        else:
            lost_influence_on_bluff = player_being_challenged.lose_influence()
            message = (f"Desafio teve sucesso! {player_being_challenged.name} não tinha '{required_character}' e perdeu '{lost_influence_on_bluff}'.")
            return message, True

class Block:
    pass