WEAPONS = {
    "Espada Básica": {"ataque": 15, "sprite": "assets/sprites/items/arma_espada_basica.png"},
    "Adaga Rápida": {"ataque": 10, "sprite": "assets/sprites/items/arma_adaga_rapida.png"},
    "Arco Longo": {"ataque": 18, "sprite": "assets/sprites/items/arma_arco_longo.png"},
    "Machado Pesado": {"ataque": 25, "sprite": "assets/sprites/items/arma_machado_pesado.png"},
    "Cajado Mágico": {"ataque": 12, "sprite": "assets/sprites/items/arma_cajado_magico.png"},
}

ARMORS = {
    "Couro Simples": {"defesa": 2, "sprite": "assets/sprites/items/armadura_couro_simples.png"},
    "Escudo de Madeira": {"defesa": 3, "sprite": "assets/sprites/items/armadura_escudo_madeira.png"},
    "Placa de Ferro": {"defesa": 5, "sprite": "assets/sprites/items/armadura_placa_ferro.png"},
    "Capacete Guerreiro": {"defesa": 4, "sprite": "assets/sprites/items/armadura_capacete_guerreiro.png"},
    "Manto Mágico": {"defesa": 3, "sprite": "assets/sprites/items/armadura_manto_magico.png"},
}

SPELLS = {
    "Bola de Fogo": {"dano": 35, "custo": 10, "sprite": "assets/sprites/items/item_magia_bola_fogo.png"},
    "Raio": {"dano": 28, "custo": 8, "sprite": "assets/sprites/items/item_magia_raio.png"},
    "Escudo de Gelo": {"dano": 0, "custo": 6, "sprite": "assets/sprites/items/item_magia_escudo_gelo.png"},
    "Cura Maior": {"dano": 0, "custo": 10, "sprite": "assets/sprites/items/item_magia_cura_maior.png"},
    "Teleporte": {"dano": 0, "custo": 12, "sprite": "assets/sprites/items/item_magia_teleporte.png"},
}

POTIONS = {
    "Poção Cura Pequena": {"cura": 60, "sprite": "assets/sprites/items/item_pocao_cura_pequena.png"},
    "Poção Mana Pequena": {"mana": 30, "sprite": "assets/sprites/items/item_pocao_mana_pequena.png"},
    "Poção Força": {"ataque": 15, "duracao": 3, "sprite": "assets/sprites/items/item_pocao_forca.png"},
    "Poção Defesa": {"defesa": 10, "duracao": 3, "sprite": "assets/sprites/items/item_pocao_defesa.png"},
    "Poção Veneno": {"dano": 40, "sprite": "assets/sprites/items/item_pocao_veneno.png"},
}

CONSUMABLES = {
    "Bandagem": {"cura": 25, "sprite": "assets/sprites/items/item_consumivel_bandagem.png"},
    "Comida Simples": {"cura": 35, "sprite": "assets/sprites/items/item_consumivel_comida_simples.png"},
    "Fruta Mágica": {"mana": 40, "sprite": "assets/sprites/items/item_consumivel_fruta_magica.png"},
    "Pergaminho Ataque": {"ataque": 12, "sprite": "assets/sprites/items/item_consumivel_pergaminho_ataque.png"},
    "Pergaminho Defesa": {"defesa": 8, "sprite": "assets/sprites/items/item_consumivel_pergaminho_defesa.png"},
}


ENEMIES = {
    "Caverna": {
        "regular": [
            {"nome": "Goblin", "vida": 35, "ataque": 8, "defesa": 2, "sprite": "assets/sprites/enemies/dungeon cave/goblin.png"},
            {"nome": "Aranha Venenosa", "vida": 28, "ataque": 10, "defesa": 1, "sprite": "assets/sprites/enemies/dungeon cave/aranha_venenosa.png"},
            {"nome": "Zumbi", "vida": 40, "ataque": 7, "defesa": 4, "sprite": "assets/sprites/enemies/dungeon cave/zumbi.png"},
        ],
        "boss": {"nome": "Goblin King", "vida": 110, "ataque": 13, "defesa": 5, "sprite": "assets/sprites/enemies/dungeon cave/goblin_king.png"}
    },
    "Desértica": {
        "regular": [
            {"nome": "Bandido do Deserto", "vida": 38, "ataque": 9, "defesa": 3, "sprite": "assets/sprites/enemies/dungeon desert/bandido_do_deserto.png"},
            {"nome": "Escorpião", "vida": 34, "ataque": 11, "defesa": 2, "sprite": "assets/sprites/enemies/dungeon desert/escorpiao.png"},
            {"nome": "Múmia", "vida": 42, "ataque": 8, "defesa": 5, "sprite": "assets/sprites/enemies/dungeon desert/mumia.png"},
        ],
        "boss": {"nome": "Scorpion Queen", "vida": 120, "ataque": 15, "defesa": 4, "sprite": "assets/sprites/enemies/dungeon desert/scorpion_queen.png"}
    },
    "Tecnológica": {
        "regular": [
            {"nome": "Drone de Vigilância", "vida": 32, "ataque": 9, "defesa": 4, "sprite": "assets/sprites/enemies/dungeon tech/drone_de_vigilancia.png"},
            {"nome": "Robô de Limpeza Hostil", "vida": 38, "ataque": 10, "defesa": 4, "sprite": "assets/sprites/enemies/dungeon tech/robo_de_limpeza_hostil.png"},
            {"nome": "Torreta Desativada", "vida": 36, "ataque": 12, "defesa": 3, "sprite": "assets/sprites/enemies/dungeon tech/torreta_desativada.png"},
        ],
        "boss": {"nome": "Cyber Golem", "vida": 130, "ataque": 16, "defesa": 6, "sprite": "assets/sprites/enemies/dungeon tech/cyber_golem.png"}
    },
    "Mal Assombrada": {
        "regular": [
            {"nome": "Fantasma", "vida": 30, "ataque": 10, "defesa": 3, "sprite": "assets/sprites/enemies/dungeon mal assombrada/fantasma.png"},
            {"nome": "Gárgula", "vida": 40, "ataque": 11, "defesa": 4, "sprite": "assets/sprites/enemies/dungeon mal assombrada/gargula.png"},
            {"nome": "Morcego Gigante", "vida": 34, "ataque": 9, "defesa": 3, "sprite": "assets/sprites/enemies/dungeon mal assombrada/morcego_gigante.png"},
        ],
        "boss": {"nome": "Poltergeist", "vida": 125, "ataque": 14, "defesa": 5, "sprite": "assets/sprites/enemies/dungeon mal assombrada/poltergeist.png"}
    },
    "Final": {
        "regular": [],
        "boss": {"nome": "Divine Entity", "vida": 200, "ataque": 18, "defesa": 7, "sprite": "assets/sprites/enemies/Final/divine_entity.png"}
    }
}


DROPS = {
    "Caverna": {
        "armas": {"chance": 15, "itens": ["Espada Básica", "Adaga Rápida"]},
        "armaduras": {"chance": 15, "itens": ["Couro Simples", "Escudo de Madeira"]},
        "poções": {"chance": 60, "itens": ["Poção Cura Pequena", "Poção Mana Pequena"]},
        "consumíveis": {"chance": 30, "itens": ["Bandagem", "Comida Simples"]},
        "ouro": {"chance": 40, "min": 10, "max": 25}
    },
    "Desértica": {
        "armas": {"chance": 20, "itens": ["Arco Longo", "Machado Pesado"]},
        "armaduras": {"chance": 20, "itens": ["Escudo de Madeira", "Placa de Ferro"]},
        "poções": {"chance": 65, "itens": ["Poção Cura Pequena", "Poção Força"]},
        "consumíveis": {"chance": 35, "itens": ["Comida Simples", "Fruta Mágica"]},
        "ouro": {"chance": 45, "min": 20, "max": 40}
    },
    "Tecnológica": {
        "armas": {"chance": 25, "itens": ["Cajado Mágico", "Arco Longo"]},
        "armaduras": {"chance": 25, "itens": ["Placa de Ferro", "Capacete Guerreiro"]},
        "poções": {"chance": 70, "itens": ["Poção Mana Pequena", "Poção Defesa"]},
        "consumíveis": {"chance": 40, "itens": ["Fruta Mágica", "Pergaminho Ataque"]},
        "ouro": {"chance": 50, "min": 30, "max": 50}
    },
    "Mal Assombrada": {
        "armas": {"chance": 25, "itens": ["Machado Pesado", "Cajado Mágico"]},
        "armaduras": {"chance": 25, "itens": ["Capacete Guerreiro", "Manto Mágico"]},
        "poções": {"chance": 75, "itens": ["Poção Força", "Poção Defesa"]},
        "consumíveis": {"chance": 45, "itens": ["Pergaminho Ataque", "Pergaminho Defesa"]},
        "ouro": {"chance": 55, "min": 40, "max": 60}
    },
    "Final": {
        "armas": {"chance": 100, "itens": ["Machado Pesado", "Cajado Mágico"]},
        "armaduras": {"chance": 100, "itens": ["Manto Mágico"]},
        "poções": {"chance": 100, "itens": ["Poção Cura Pequena"]},
        "consumíveis": {"chance": 100, "itens": ["Pergaminho Defesa"]},
        "ouro": {"chance": 100, "min": 100, "max": 150}
    }
}

DUNGEONS = [
    {"nome": "Caverna", "arquivo": "assets/tiles/Dungeon_Cave_Map.jpg"},
    {"nome": "Desértica", "arquivo": "assets/tiles/Dungeon_Desert_Map.jpg"},
    {"nome": "Tecnológica", "arquivo": "assets/tiles/Dungeon_Tech.jpeg"},
    {"nome": "Mal Assombrada", "arquivo": "assets/tiles/Dungeon_Haunted_Map.jpg"},
    {"nome": "Final", "arquivo": "assets/tiles/Dungeon_Boss_Final_Map.jpg"},
]