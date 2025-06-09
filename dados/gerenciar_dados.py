def salvar_jogo(estado, arquivo):
    """
    Salva o estado do jogo em um arquivo.
    
    :param estado: Dicionário com o estado do jogo.
    :param arquivo: Caminho do arquivo onde o estado será salvo.
    """
    import json
    with open(arquivo, 'w') as f:
        json.dump(estado, f)

def carregar_jogo(arquivo):
    """
    Carrega o estado do jogo de um arquivo.
    
    :param arquivo: Caminho do arquivo de onde o estado será carregado.
    :return: Dicionário com o estado do jogo.
    """
    import json
    try:
        with open(arquivo, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        
        return None