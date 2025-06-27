import json
import random
from typing import List, Dict
from pathlib import Path

class Deck:
    """Classe que gerencia o baralho do jogo Coup com persistência em JSON"""
    
    def __init__(self, json_file: str = "deck_state.json"):
        self._json_file = json_file
        self._cards = []
        self._discard_pile = []
        
        if Path(json_file).exists():
            self._load_from_json()
        else:
            self._initialize_new_deck()
    
    def _initialize_new_deck(self) -> None:
        """Cria um baralho novo com as cartas padroes do Coup."""
        # CORREÇÃO: Nomes em português para combinar com os arquivos de imagem em setup.py
        characters = ["Duque", "Assassino", "Capitao", "Embaixador", "Condessa"]
        self._cards = []
        card_id = 1
        for character in characters:
            for _ in range(3):
                self._cards.append({"id": card_id, "character": character, "in_game": False})
                card_id += 1

        self._discard_pile = []
        self.shuffle()
        # Salva o estado inicial correto
        self._save_to_json()
    
    def _load_from_json(self) -> None:
        """Carrega o estado do baralho do JSON."""
        try:
            with open(self._json_file, 'r') as f:
                data = json.load(f)
                self._cards = data.get('cards', [])
                self._discard_pile = data.get('discard_pile', [])
            
            # CORREÇÃO: Auto-correção para arquivos de estado vazios ou corrompidos
            if not self._cards and not self._discard_pile:
                print("AVISO: O estado salvo do baralho está vazio. Criando um novo baralho.")
                self._initialize_new_deck()

        except Exception as e:
            print(f"Erro ao carregar deck: {e}. Criando um novo baralho.")
            self._initialize_new_deck()
    
    def _save_to_json(self) -> None:
        """Salva o estado atual do baralho em JSON."""
        data = {
            "cards": self._cards,
            "discard_pile": self._discard_pile
        }
        try:
            with open(self._json_file, 'w') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar deck: {e}")
    
    def shuffle(self) -> None:
        random.shuffle(self._cards)
        self._save_to_json()
    
    def draw(self, count: int = 1) -> List[Dict]:
        count = min(count, len(self._cards))
        drawn = self._cards[:count]
        self._cards = self._cards[count:]
        for card in drawn:
            card["in_game"] = True
        self._save_to_json()
        return drawn
    
    def discard(self, card: Dict) -> None:
        card["in_game"] = False
        self._discard_pile.append(card)
        self._save_to_json()
    
    def return_cards(self, cards: List[Dict]) -> None:
        for card in cards:
            card["in_game"] = False
            if card in self._discard_pile:
                self._discard_pile.remove(card)
        self._cards.extend(cards)
        self.shuffle()