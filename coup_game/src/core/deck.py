from Carta import Carta
import json
import random as rand
class Deck:
    

    def __init__(self, cartas: list, descarte: list,)
        with open("data/characters.json", encoding="utf-8") as f:
            dados = json.load(f)

        for personagem in self.dados:
            nome = personagem["nome"]
            descricao = personagem["descricao"]
            # Criar 3 cartas de cada tipo
            for i in range(3):
                self._cartas.append(Carta(nome, descricao))
        
        self._descarte = []

    def embaralhar(self):
        rand.shuffle(self._cartas)

    def troca_embaixador(self):
        pass
    
    def distribuir(self):
        i=0
        while (i<4):
            j=0
            while(j<2):
                self._cartas.pop()
                """""
                    função que manda cartas para o jogador
                """
                j+=1
            i +=1      

    def descartar(self, carta:Carta):
        if(carta.virada==True):
            self._cartas.remove(carta)
            self._descarte.append(carta)
    
        




