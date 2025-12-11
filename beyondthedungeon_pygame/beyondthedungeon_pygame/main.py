import pygame
import random
import time
import math
import os
from enum import Enum
from game_data import DUNGEONS, ENEMIES, WEAPONS, ARMORS, SPELLS, POTIONS, CONSUMABLES, DROPS
from inventory import Inventario, InventarioUI, Item
from settings import Configuracoes, TelaConfiguracao
from collision import CollisionMap
from ranking import RankingManager, RankingUI
from hud import HUD

def truncate_text(text, max_width, font):
    if font.size(text)[0] <= max_width:
        return text
    while len(text) > 0 and font.size(text + "...")[0] > max_width:
        text = text[:-1]
    return text + "..." if len(text) > 0 else "..."

pygame.init()
pygame.mixer.init()

VIRTUAL_WIDTH = 1280
VIRTUAL_HEIGHT = 720
DUNGEON_SIZE = 1280
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 100, 200)
YELLOW = (255, 215, 0)
GOLD = (218, 165, 32)
ORANGE = (255, 140, 0)
PURPLE = (128, 0, 128)

class GameState(Enum):
    INTRO = 0
    MENU = 1
    PLAYING = 2
    COMBAT = 3
    INVENTORY = 4
    GAME_OVER = 5
    VICTORY = 6
    SETTINGS = 7
    TRANSITION = 8
    PAUSED = 9

class TipoDano(Enum):
    NORMAL = 1
    CRITICO = 2
    FRACO = 3
    ESPECIAL = 4
    CURA = 5

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.music_volume = 0.5
        self.sfx_volume = 0.5
        self.current_music = None
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.load_sound("hit", "assets/audio/sfx/hit.wav")
        self.load_sound("sword", "assets/audio/sfx/sword.wav")
        self.load_sound("select", "assets/audio/sfx/select.wav")
        self.load_sound("magic", "assets/audio/sfx/magic.wav")
        self.load_sound("equip", "assets/audio/sfx/select.wav")
        
    def load_sound(self, name, relative_path):
        full_path = os.path.join(self.base_dir, relative_path)
        if os.path.exists(full_path):
            try:
                sound = pygame.mixer.Sound(full_path)
                sound.set_volume(self.sfx_volume)
                self.sounds[name] = sound
            except: pass

    def update_volume(self, music_percent, sfx_percent, music_enabled, sfx_enabled):
        self.music_volume = music_percent / 100.0
        self.sfx_volume = sfx_percent / 100.0
        
        if not music_enabled:
            pygame.mixer.music.set_volume(0)
        else:
            pygame.mixer.music.set_volume(self.music_volume)
            if pygame.mixer.music.get_busy() == 0 and self.current_music:
                try: pygame.mixer.music.play(-1)
                except: pass

        for s in self.sounds.values():
            if not sfx_enabled:
                s.set_volume(0)
            else:
                s.set_volume(self.sfx_volume)

    def play_sound(self, name):
        if name in self.sounds:
            self.sounds[name].set_volume(self.sfx_volume)
            self.sounds[name].play()

    def play_music(self, relative_path):
        extensions = ["", ".mp3", ".ogg", ".wav"]
        full_path = ""
        found = False
        
        for ext in extensions:
            test_path = os.path.join(self.base_dir, f"assets/audio/music/{relative_path}{ext}")
            if os.path.exists(test_path):
                full_path = test_path
                found = True
                break
        
        if not found: return

        if self.current_music == full_path and pygame.mixer.music.get_busy():
            return
        
        try:
            pygame.mixer.music.load(full_path)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1)
            self.current_music = full_path
        except Exception as e:
            print(f"Erro ao tocar musica: {e}")

    def stop_music(self):
        pygame.mixer.music.stop()
        self.current_music = None

class Character:
    def __init__(self, nome, vida, ataque, defesa):
        self.nome = nome
        self.vida = vida
        self.vida_max = vida
        self.ataque_base = ataque
        self.defesa_base = defesa
        self.mana = 50
        self.mana_max = 50
        self.x = 0
        self.y = 0
        self.sprite = None
        self.equipamentos = {"arma": None, "armadura": None}
    
    @property
    def ataque(self):
        bonus = self.equipamentos["arma"]["ataque"] if self.equipamentos["arma"] else 0
        return self.ataque_base + bonus
    
    @property
    def defesa(self):
        bonus = self.equipamentos["armadura"]["defesa"] if self.equipamentos["armadura"] else 0
        return self.defesa_base + bonus
    
    def receber_dano(self, dano):
        dano_final = max(1, dano - self.defesa)
        self.vida -= dano_final
        if self.vida < 0: self.vida = 0
        return dano_final
    
    def curar(self, quantidade):
        self.vida = min(self.vida_max, self.vida + quantidade)
    
    def restaurar_mana(self, quantidade):
        self.mana = min(self.mana_max, self.mana + quantidade)
    
    def esta_vivo(self):
        return self.vida > 0

class InputManager:
    def __init__(self):
        self.last_key_press = {}
        self.key_delay = 180 
        self.keys_pressed_this_frame = set()
    
    def update(self, keys):
        self.keys_pressed_this_frame = set()
        current_time = pygame.time.get_ticks()
        
        teclas = [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, 
                  pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_i, pygame.K_TAB, pygame.K_q, pygame.K_BACKSPACE]
        
        for key in teclas:
            if keys[key]: self.keys_pressed_this_frame.add(key)
        
        for key in list(self.last_key_press.keys()):
            if current_time - self.last_key_press[key] > self.key_delay * 3:
                del self.last_key_press[key]
    
    def is_key_pressed(self, key, delay=None):
        if delay is None: delay = self.key_delay
        if key not in self.keys_pressed_this_frame: return False
        
        current_time = pygame.time.get_ticks()
        if key not in self.last_key_press:
            self.last_key_press[key] = current_time - delay - 1
        
        if current_time - self.last_key_press[key] > delay:
            self.last_key_press[key] = current_time
            return True
        return False

class Player(Character):
    def __init__(self):
        super().__init__("Rey", 160, 18, 8)
        self.inventario = Inventario()
        self.sprite_frames = {"down": [], "up": [], "left": [], "right": []}
        self.frame_atual = 0
        self.direcao = "down"
        self.animacao_contador = 0
        self.velocidade = 5
        self.passos = 0
        self.load_sprites()
        self.ouro = 0
    
    def load_sprites(self):
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            mapeamento = {"walk_back": "up", "walk_front": "left", "walk_side": "right"}

            for arquivo, chave_direcao in mapeamento.items():
                frames = []
                for i in range(1, 5): 
                    path = os.path.join(base_dir, f"assets/sprites/player/{arquivo}_{i}.png")
                    try:
                        img = pygame.image.load(path).convert_alpha()
                        img = pygame.transform.scale(img, (48, 48))
                        frames.append(img)
                    except: pass
                if frames: self.sprite_frames[chave_direcao] = frames
                else: self.sprite_frames[chave_direcao] = [pygame.Surface((48, 48))]

            path_frente = os.path.join(base_dir, "assets/sprites/player/walk_front_1.png")
            try:
                img_frente = pygame.image.load(path_frente).convert_alpha()
                img_frente = pygame.transform.scale(img_frente, (48, 48))
                self.sprite_frames["down"] = [img_frente]
            except: self.sprite_frames["down"] = [pygame.Surface((48, 48))]

            self.sprite = self.sprite_frames["down"][0]
        except: pass
    
    def update(self, keys, dungeon_width, dungeon_height, collision_map, input_manager):
        movimento = False
        old_x, old_y = self.x, self.y
        
        if keys[pygame.K_UP]:
            self.y = max(0, self.y - self.velocidade)
            self.direcao = "up"
            movimento = True
        elif keys[pygame.K_DOWN]:
            self.y = min(dungeon_height - 48, self.y + self.velocidade)
            self.direcao = "down"
            movimento = True
            
        if keys[pygame.K_LEFT]:
            self.x = max(0, self.x - self.velocidade)
            self.direcao = "left"
            movimento = True
        elif keys[pygame.K_RIGHT]:
            self.x = min(dungeon_width - 48, self.x + self.velocidade)
            self.direcao = "right"
            movimento = True
        
        if collision_map and movimento:
            if not collision_map.is_passable(self.x, self.y):
                self.x, self.y = old_x, old_y
                movimento = False
        
        if movimento:
            self.passos += 1
            self.animacao_contador += 0.15
            total_frames = len(self.sprite_frames[self.direcao])
            if total_frames > 1:
                if self.animacao_contador >= 1:
                    self.animacao_contador = 0
                    self.frame_atual = (self.frame_atual + 1) % total_frames
                self.sprite = self.sprite_frames[self.direcao][self.frame_atual]
            else:
                self.sprite = self.sprite_frames[self.direcao][0]
        else:
            self.frame_atual = 0
            if self.sprite_frames[self.direcao]:
                self.sprite = self.sprite_frames[self.direcao][0]
        
        return movimento
    
    def draw(self, screen, camera_x, camera_y):
        screen.blit(self.sprite, (self.x - camera_x, self.y - camera_y))

class Enemy(Character):
    def __init__(self, dados):
        super().__init__(dados["nome"], dados["vida"], dados["ataque"], dados["defesa"])
        self.sprite_path = dados["sprite"]
        self.load_sprite()
    
    def load_sprite(self):
        try:
            self.sprite = pygame.image.load(self.sprite_path).convert_alpha()
            self.sprite = pygame.transform.scale(self.sprite, (96, 96))
        except:
            self.sprite = pygame.Surface((96, 96))
            self.sprite.fill(RED)

class Combat:
    def __init__(self, player, enemy, dificuldade="Normal", dungeon_nome="Caverna", sound_manager=None):
        self.player = player
        self.enemy = enemy
        self.dungeon_nome = dungeon_nome
        self.sound_manager = sound_manager
        self.turno = "player"
        self.log = []
        self.log.append(f"Um {self.enemy.nome} hostil apareceu!")
        self.animacao_timer = 0
        self.mostrar_dano = False
        self.dano_mostrado = 0
        self.dano_tipo = TipoDano.NORMAL
        self.dano_cor = WHITE
        
        multiplicador = {"Fácil": 0.8, "Normal": 1.0, "Difícil": 1.4}[dificuldade]
        self.enemy.vida = int(self.enemy.vida * multiplicador)
        self.enemy.vida_max = self.enemy.vida
        self.enemy.ataque_base = int(self.enemy.ataque_base * multiplicador)
        
        self.opcoes = ["Lutar", "Magia", "Poção", "Fugir"]
        self.opcao_selecionada = 0
        self.em_menu = True
        self.atualizar_listas()

        self.PANEL_BG = (20, 20, 30, 230)
        self.BORDER_COLOR = (180, 160, 100)
        self.TEXT_COLOR = (240, 240, 240)
        self.HIGHLIGHT_COLOR = (255, 215, 0)
        
        if self.sound_manager:
            self.sound_manager.play_music("battle_theme")

    def atualizar_listas(self):
        self.magias_disponiveis = [i.nome for i in self.player.inventario.itens if i.tipo == "magia"]
        self.pocoes_disponiveis = [i.nome for i in self.player.inventario.itens if i.tipo == "pocao"]

    def calcular_dano(self, ataque):
        return ataque + random.randint(-2, 3)
    
    def ataque_player(self):
        dano_base = self.calcular_dano(self.player.ataque)
        eh_critico = random.random() < 0.20
        if eh_critico:
            dano_base = int(dano_base * 1.5)
            self.dano_tipo = TipoDano.CRITICO
            self.dano_cor = GOLD
            mensagem = f"Crítico! {self.enemy.nome} tomou {self.enemy.receber_dano(dano_base)} de dano!"
        else:
            self.dano_tipo = TipoDano.NORMAL
            self.dano_cor = YELLOW
            mensagem = f"Rey causou {self.enemy.receber_dano(dano_base)} de dano."
        
        if self.sound_manager: self.sound_manager.play_sound("sword")
        self.log.append(mensagem)
        self.mostrar_dano = True
        self.dano_mostrado = dano_base
        self.animacao_timer = 60
        self.em_menu = False
    
    def ataque_inimigo(self):
        if random.random() < 0.30:
            ataque_especial = random.choice([("Investida", 1.3), ("Golpe Duplo", 1.2), ("Veneno", 1.1)])
            nome, mult = ataque_especial
            dano_base = int(self.calcular_dano(self.enemy.ataque) * mult)
            self.dano_tipo = TipoDano.ESPECIAL
            self.dano_cor = ORANGE
            msg = f"{self.enemy.nome} usou {nome}!"
        else:
            dano_base = self.calcular_dano(self.enemy.ataque)
            self.dano_tipo = TipoDano.NORMAL
            self.dano_cor = RED
            msg = f"{self.enemy.nome} atacou!"

        dano_final = self.player.receber_dano(dano_base)
        if self.sound_manager: self.sound_manager.play_sound("hit")
        self.log.append(f"{msg} Dano recebido: {dano_final}")
        self.mostrar_dano = True
        self.dano_mostrado = dano_final
        self.animacao_timer = 60
    
    def usar_magia(self, magia_nome):
        if magia_nome in SPELLS:
            magia = SPELLS[magia_nome]
            if self.player.mana >= magia["custo"]:
                self.player.mana -= magia["custo"]
                if magia["dano"] > 0:
                    dano = random.randint(magia["dano"] - 2, magia["dano"] + 2)
                    dano_final = self.enemy.receber_dano(dano)
                    self.log.append(f"Magia {magia_nome}! Dano: {dano_final}")
                    self.dano_tipo = TipoDano.ESPECIAL
                    self.dano_cor = PURPLE
                else:
                    self.player.curar(30)
                    self.log.append(f"Magia {magia_nome}! Vida recuperada.")
                    self.dano_tipo = TipoDano.CURA
                    self.dano_mostrado = 30
                
                if self.sound_manager: self.sound_manager.play_sound("magic")
                self.mostrar_dano = True
                self.animacao_timer = 60
                self.em_menu = False
                return True
            else:
                self.log.append("Mana insuficiente!")
        return False
    
    def usar_pocao(self, pocao_nome):
        idx = -1
        item_obj = None
        for i, item in enumerate(self.player.inventario.itens):
            if item.nome == pocao_nome and item.tipo == "pocao":
                idx = i
                item_obj = item
                break
        
        if idx != -1 and item_obj:
            dados = item_obj.dados
            used = False
            
            if "cura" in dados:
                self.player.curar(dados["cura"])
                self.log.append(f"Usou {pocao_nome}. HP +{dados['cura']}")
                self.dano_tipo = TipoDano.CURA
                self.dano_mostrado = dados["cura"]
                self.mostrar_dano = True
                self.animacao_timer = 60
                used = True
            
            if "mana" in dados:
                self.player.restaurar_mana(dados["mana"])
                self.log.append(f"Usou {pocao_nome}. MP +{dados['mana']}")
                used = True
                
            if "dano" in dados:
                dano = dados["dano"]
                dano_final = self.enemy.receber_dano(dano)
                self.log.append(f"Jogou {pocao_nome}! Inimigo sofreu {dano_final}")
                self.dano_tipo = TipoDano.ESPECIAL
                self.dano_mostrado = dano_final
                self.mostrar_dano = True
                self.animacao_timer = 60
                used = True

            if used:
                self.player.inventario.remover_item(idx)
                self.atualizar_listas()
                if self.sound_manager: self.sound_manager.play_sound("magic")
                self.em_menu = False
                return True
        return False

    def tentar_fugir(self):
        if random.randint(1, 100) > 40:
            self.log.append("Escapou com sucesso!")
            return True
        self.log.append("Fuga falhou!")
        self.em_menu = False
        return False

    def gerar_drops(self):
        import random
        if self.dungeon_nome not in DROPS: return []
        drops_config = DROPS[self.dungeon_nome]
        tipos = list(drops_config.keys())
        pesos = [drops_config[k]["chance"] for k in tipos]
        
        qtd_drops = 1
        if random.random() < 0.3: qtd_drops = 2

        drops_gerados = []
        for _ in range(qtd_drops):
            tipo_escolhido = random.choices(tipos, weights=pesos, k=1)[0]
            config = drops_config[tipo_escolhido]
            
            if tipo_escolhido == "ouro":
                drops_gerados.append(("ouro", random.randint(config["min"], config["max"])))
            else:
                item_nome = random.choice(config["itens"])
                drops_gerados.append((tipo_escolhido, item_nome))
        return drops_gerados

    def draw(self, screen, font_small, font_medium, font_large):
        w, h = screen.get_width(), screen.get_height()
        
        for y in range(h):
            c = int(20 + (y / h) * 40)
            pygame.draw.line(screen, (c, c, c+10), (0, y), (w, y))
        
        pygame.draw.ellipse(screen, (10, 10, 15), (w*0.6, h*0.35, 400, 100))
        pygame.draw.ellipse(screen, (10, 10, 15), (w*0.1, h*0.55, 400, 100))

        if self.enemy.sprite:
            enemy_scale = pygame.transform.scale(self.enemy.sprite, (250, 250))
            enemy_rect = enemy_scale.get_rect(center=(w * 0.75, h * 0.35))
            screen.blit(enemy_scale, enemy_rect)

        if self.player.sprite_frames["down"]:
            player_sprite = self.player.sprite_frames["down"][0]
            player_scale = pygame.transform.scale(player_sprite, (220, 220))
            player_rect = player_scale.get_rect(center=(w * 0.25, h * 0.55))
            screen.blit(player_scale, player_rect)

        self.draw_unit_hud(screen, self.enemy, 50, 50, font_medium, False)

        panel_h = 180
        panel_y = h - panel_h
        
        s = pygame.Surface((w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(s, self.PANEL_BG, s.get_rect())
        screen.blit(s, (0, panel_y))
        pygame.draw.line(screen, self.BORDER_COLOR, (0, panel_y), (w, panel_y), 4)
        
        stats_w = 320 
        self.draw_player_stats_panel(screen, 20, panel_y + 20, stats_w, panel_h - 40, font_medium, font_small)
        
        log_x = stats_w + 40
        log_w = w - stats_w - 300 - 60 
        self.draw_log_panel(screen, log_x, panel_y + 20, log_w, panel_h - 40, font_small)
        
        menu_w = 280 
        menu_x = w - menu_w - 20
        if self.em_menu:
            self.draw_action_menu(screen, menu_x, panel_y + 20, menu_w, panel_h - 40, font_medium)

        if self.mostrar_dano and self.animacao_timer > 0:
            offset_y = (60 - self.animacao_timer) * 3
            font_dano = pygame.font.Font(None, int(60 + (self.animacao_timer/60)*20))
            prefix = ""
            if self.dano_tipo == TipoDano.CURA: prefix = "+"
            txt = f"{prefix}{self.dano_mostrado}"
            color = GREEN if self.dano_tipo == TipoDano.CURA else self.dano_cor
            if self.dano_tipo == TipoDano.CRITICO: txt += "!"
            dano_sombra = font_dano.render(txt, True, BLACK)
            dano_text = font_dano.render(txt, True, color)
            
            if self.turno == "player":
                if self.dano_tipo == TipoDano.CURA: target_pos = (w * 0.25, h * 0.55 - 50)
                else: target_pos = (w * 0.75, h * 0.35 - 50)
            else: target_pos = (w * 0.25, h * 0.55 - 50)

            rect_dano = dano_text.get_rect(center=(target_pos[0], target_pos[1] - offset_y))
            screen.blit(dano_sombra, (rect_dano.x+2, rect_dano.y+2))
            screen.blit(dano_text, rect_dano)

    def draw_unit_hud(self, screen, unit, x, y, font, is_player):
        w, h = 350, 80
        rect = pygame.Rect(x, y, w, h)
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(s, self.PANEL_BG, s.get_rect(), border_radius=8)
        screen.blit(s, (x, y))
        pygame.draw.rect(screen, self.BORDER_COLOR, rect, 2, border_radius=8)
        name_txt = font.render(unit.nome, True, self.HIGHLIGHT_COLOR)
        screen.blit(name_txt, (x + 15, y + 10))
        bar_x = x + 15
        bar_y = y + 45
        bar_w = w - 30
        bar_h = 12
        pct = unit.vida / unit.vida_max
        pygame.draw.rect(screen, (50,0,0), (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(screen, RED if pct < 0.3 else GREEN, (bar_x, bar_y, bar_w * pct, bar_h))
        pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_w, bar_h), 1)

    def draw_player_stats_panel(self, screen, x, y, w, h, font_name, font_bar):
        name_txt = font_name.render(self.player.nome, True, self.HIGHLIGHT_COLOR)
        screen.blit(name_txt, (x, y))
        hp_y = y + 50
        hp_pct = self.player.vida / self.player.vida_max
        pygame.draw.rect(screen, (50,0,0), (x, hp_y, w, 15))
        pygame.draw.rect(screen, RED if hp_pct < 0.3 else GREEN, (x, hp_y, w * hp_pct, 15))
        pygame.draw.rect(screen, GRAY, (x, hp_y, w, 15), 1)
        hp_txt = font_bar.render(f"HP {int(self.player.vida)}/{self.player.vida_max}", True, WHITE)
        screen.blit(hp_txt, (x, hp_y - 22))
        mp_y = y + 100
        mp_pct = self.player.mana / self.player.mana_max
        pygame.draw.rect(screen, (0,0,50), (x, mp_y, w, 15))
        pygame.draw.rect(screen, BLUE, (x, mp_y, w * mp_pct, 15))
        pygame.draw.rect(screen, GRAY, (x, mp_y, w, 15), 1)
        mp_txt = font_bar.render(f"MP {int(self.player.mana)}/{self.player.mana_max}", True, WHITE)
        screen.blit(mp_txt, (x, mp_y - 22))

    def draw_log_panel(self, screen, x, y, w, h, font):
        pygame.draw.line(screen, self.BORDER_COLOR, (x - 20, y), (x - 20, y + h), 2)
        msgs = self.log[-4:]
        for i, msg in enumerate(msgs):
            col = WHITE if i == len(msgs)-1 else GRAY
            txt_str = truncate_text(msg, w, font)
            txt = font.render(txt_str, True, col)
            screen.blit(txt, (x, y + i * 30))

    def draw_action_menu(self, screen, x, y, w, h, font):
        pygame.draw.line(screen, self.BORDER_COLOR, (x - 20, y), (x - 20, y + h), 2)
        btn_w = w // 2 - 10
        btn_h = 45
        for i, op in enumerate(self.opcoes):
            col = i % 2
            row = i // 2
            bx = x + col * (btn_w + 10)
            by = y + row * (btn_h + 15)
            color = self.TEXT_COLOR
            prefix = ""
            if i == self.opcao_selecionada:
                color = self.HIGHLIGHT_COLOR
                prefix = "> "
            txt = font.render(prefix + op, True, color)
            screen.blit(txt, (bx, by))

class Game:
    def __init__(self):
        self.configuracoes = Configuracoes()
        self.virtual_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
        self.screen = None
        self.aplicar_configuracoes()
        pygame.display.set_caption("Beyond the Dungeon")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.MENU
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.sound_manager = SoundManager()
        self.menu_background = None
        bg_path = os.path.join(base_dir, "assets", "tiles", "fundo.png")
        if os.path.exists(bg_path):
            try:
                img = pygame.image.load(bg_path).convert()
                self.menu_background = pygame.transform.scale(img, (VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
            except: pass
        font_path = os.path.join(base_dir, "assets", "BoldPixels.ttf")
        size_large, size_medium, size_small = 64, 32, 24
        if os.path.exists(font_path):
            try:
                self.font_large = pygame.font.Font(font_path, size_large)
                self.font_medium = pygame.font.Font(font_path, size_medium)
                self.font_small = pygame.font.Font(font_path, size_small)
            except:
                self.font_large = pygame.font.Font(None, 72)
                self.font_medium = pygame.font.Font(None, 48)
                self.font_small = pygame.font.Font(None, 32)
        else:
            self.font_large = pygame.font.Font(None, 72)
            self.font_medium = pygame.font.Font(None, 48)
            self.font_small = pygame.font.Font(None, 32)
        self.input_manager = InputManager()
        self.tela_config = TelaConfiguracao(VIRTUAL_WIDTH, VIRTUAL_HEIGHT, self.configuracoes)
        self.player = Player()
        self.player.inventario.adicionar_item("Espada Básica", "arma", WEAPONS["Espada Básica"])
        self.player.inventario.adicionar_item("Poção Cura Pequena", "pocao", POTIONS["Poção Cura Pequena"])
        self.player.inventario.adicionar_item("Bola de Fogo", "magia", SPELLS["Bola de Fogo"])
        self.player.equipamentos["arma"] = WEAPONS["Espada Básica"]
        self.dungeon_index = 0
        self.dungeon_image = None
        self.collision_map = None
        self.boss = None
        self.combate_atual = None
        self.camera_x = 0
        self.camera_y = 0
        self.menu_opcoes = ["Jogar", "Configuracoes", "Ranking", "Sair"]
        self.menu_selecionado = 0
        self.inventario_ui = InventarioUI(VIRTUAL_WIDTH, VIRTUAL_HEIGHT)
        self.hud = HUD(VIRTUAL_WIDTH, VIRTUAL_HEIGHT)
        self.ranking_manager = RankingManager()
        self.ranking_ui = RankingUI(VIRTUAL_WIDTH, VIRTUAL_HEIGHT)
        self.mensagem_acao = ""
        self.mensagem_timer = 0
        self.chance_combate = 0.015
        self.tempo_inicio = None
        self.inimigos_mortos = 0
        self.delta_time = 0
        self.transition_timer = 0
        self.nome_input = ""
        self.sound_manager.play_music("menu_theme")
        self.load_dungeon()
    
    def aplicar_configuracoes(self):
        width, height = self.configuracoes.resolucao
        flags = pygame.RESIZABLE
        if self.configuracoes.fullscreen:
            flags = pygame.FULLSCREEN | pygame.DOUBLEBUF
        self.screen = pygame.display.set_mode((width, height), flags)
    
    def load_dungeon(self):
        if self.dungeon_index >= len(DUNGEONS):
            self.state = GameState.VICTORY
            return
        dungeon = DUNGEONS[self.dungeon_index]
        try:
            self.dungeon_image = pygame.image.load(dungeon["arquivo"]).convert()
        except:
            self.dungeon_image = pygame.Surface((DUNGEON_SIZE, DUNGEON_SIZE))
            self.dungeon_image.fill(DARK_GRAY)
        try:
            self.collision_map = CollisionMap(dungeon["arquivo"])
        except: self.collision_map = None
        if self.collision_map:
            self.player.x, self.player.y = self.collision_map.find_spawn_point()
            boss_x, boss_y = self.collision_map.find_boss_spawn_point()
        else:
            self.player.x, self.player.y = DUNGEON_SIZE // 2, DUNGEON_SIZE - 150
            boss_x, boss_y = DUNGEON_SIZE // 2, 100
        self.boss = Enemy(ENEMIES[dungeon["nome"]]["boss"])
        self.boss.x, self.boss.y = boss_x, boss_y
        if self.state != GameState.MENU: self.state = GameState.PLAYING
        if self.state == GameState.PLAYING:
            self.sound_manager.play_music("dungeon_ambient")
    
    def lookup_item_data(self, nome_item):
        if nome_item in WEAPONS: return "arma", WEAPONS[nome_item]
        if nome_item in ARMORS: return "armadura", ARMORS[nome_item]
        if nome_item in SPELLS: return "magia", SPELLS[nome_item]
        if nome_item in POTIONS: return "pocao", POTIONS[nome_item]
        if nome_item in CONSUMABLES: return "consumivel", CONSUMABLES[nome_item]
        return "desconhecido", {}

    def handle_settings(self, keys):
        res = self.tela_config.handle_input(keys, self.input_manager)
        if res == "voltar": self.state = GameState.MENU
        elif res == "aplicar": self.aplicar_configuracoes()
        self.sound_manager.update_volume(self.configuracoes.music_volume, self.configuracoes.sfx_volume, self.configuracoes.musica_ativada, self.configuracoes.efeitos_ativados)

    def handle_transition(self, keys):
        if self.transition_timer > 0: self.transition_timer -= 1
        if keys[pygame.K_RETURN] and self.transition_timer < 120: self.transition_timer = 0
        if self.transition_timer <= 0:
            self.dungeon_index += 1
            self.load_dungeon()
            if self.state != GameState.VICTORY:
                self.state = GameState.PLAYING

    def handle_paused(self, keys):
        if self.input_manager.is_key_pressed(pygame.K_ESCAPE):
            self.state = GameState.PLAYING
        elif self.input_manager.is_key_pressed(pygame.K_q):
            self.state = GameState.MENU
            self.sound_manager.play_music("menu_theme")

    def handle_menu(self, keys):
        if self.ranking_ui.visivel:
            self.ranking_ui.handle_input(keys)
            return
        if self.input_manager.is_key_pressed(pygame.K_UP):
            self.sound_manager.play_sound("select")
            self.menu_selecionado = (self.menu_selecionado - 1) % len(self.menu_opcoes)
        elif self.input_manager.is_key_pressed(pygame.K_DOWN):
            self.sound_manager.play_sound("select")
            self.menu_selecionado = (self.menu_selecionado + 1) % len(self.menu_opcoes)
        if self.input_manager.is_key_pressed(pygame.K_RETURN):
            self.sound_manager.play_sound("select")
            if self.menu_selecionado == 0:
                self.tempo_inicio = time.time()
                self.dungeon_index = 0
                self.player = Player()
                self.player.inventario.adicionar_item("Espada Básica", "arma", WEAPONS["Espada Básica"])
                self.player.inventario.adicionar_item("Poção Cura Pequena", "pocao", POTIONS["Poção Cura Pequena"])
                self.player.inventario.adicionar_item("Bola de Fogo", "magia", SPELLS["Bola de Fogo"])
                self.player.equipamentos["arma"] = WEAPONS["Espada Básica"]
                self.load_dungeon()
                self.state = GameState.PLAYING
                self.sound_manager.stop_music()
                self.sound_manager.play_music("dungeon_ambient")
            elif self.menu_selecionado == 1:
                self.state = GameState.SETTINGS
                self.tela_config.visivel = True
            elif self.menu_selecionado == 2:
                self.ranking_ui.visivel = True
            elif self.menu_selecionado == 3:
                self.running = False

    def handle_playing(self, keys, dt):
        res = self.inventario_ui.handle_input(keys, self.player.inventario, self.player, self.input_manager)
        if res:
            self.mensagem_acao = res
            self.mensagem_timer = 120
            if "Equipou" in res: self.sound_manager.play_sound("equip")
        if self.inventario_ui.visivel: return
        if self.input_manager.is_key_pressed(pygame.K_ESCAPE):
            self.state = GameState.PAUSED
            return
        mov = self.player.update(keys, DUNGEON_SIZE, DUNGEON_SIZE, self.collision_map, self.input_manager)
        self.camera_x = max(0, min(self.player.x - VIRTUAL_WIDTH // 2, DUNGEON_SIZE - VIRTUAL_WIDTH))
        self.camera_y = max(0, min(self.player.y - VIRTUAL_HEIGHT // 2, DUNGEON_SIZE - VIRTUAL_HEIGHT))
        
        # Lógica de Spawn com Delta Time
        if mov:
            chance_ajustada = self.chance_combate * (dt * 60)
            if random.random() < chance_ajustada:
                dg_nome = DUNGEONS[self.dungeon_index]["nome"]
                if ENEMIES[dg_nome]["regular"]:
                    en = Enemy(random.choice(ENEMIES[dg_nome]["regular"]))
                    self.combate_atual = Combat(self.player, en, self.configuracoes.dificuldade, dg_nome, self.sound_manager)
                    self.state = GameState.COMBAT

        boss_rect = pygame.Rect(self.boss.x, self.boss.y, 96, 96)
        if pygame.Rect(self.player.x, self.player.y, 48, 48).colliderect(boss_rect):
            dg_nome = DUNGEONS[self.dungeon_index]["nome"]
            self.combate_atual = Combat(self.player, Enemy(ENEMIES[dg_nome]["boss"]), self.configuracoes.dificuldade, dg_nome, self.sound_manager)
            self.state = GameState.COMBAT

    def handle_combat(self, keys):
        if self.combate_atual.em_menu:
            if self.input_manager.is_key_pressed(pygame.K_LEFT):
                self.sound_manager.play_sound("select")
                self.combate_atual.opcao_selecionada = (self.combate_atual.opcao_selecionada - 1) % 4
            elif self.input_manager.is_key_pressed(pygame.K_RIGHT):
                self.sound_manager.play_sound("select")
                self.combate_atual.opcao_selecionada = (self.combate_atual.opcao_selecionada + 1) % 4
            if self.input_manager.is_key_pressed(pygame.K_RETURN):
                self.sound_manager.play_sound("select")
                op = self.combate_atual.opcoes[self.combate_atual.opcao_selecionada]
                if op == "Lutar": self.combate_atual.ataque_player()
                elif op == "Magia" and self.combate_atual.magias_disponiveis:
                    self.combate_atual.usar_magia(self.combate_atual.magias_disponiveis[0])
                elif op == "Poção" and self.combate_atual.pocoes_disponiveis:
                    self.combate_atual.usar_pocao(self.combate_atual.pocoes_disponiveis[0])
                elif op == "Fugir":
                    if self.combate_atual.tentar_fugir():
                        self.state = GameState.PLAYING
                        self.combate_atual = None
                        self.sound_manager.stop_music()
                        self.sound_manager.play_music("dungeon_ambient")
        
        if self.combate_atual and not self.combate_atual.enemy.esta_vivo():
            if self.combate_atual.enemy.nome == self.boss.nome:
                self.state = GameState.TRANSITION
                self.transition_timer = 180
                self.combate_atual = None
                self.sound_manager.stop_music()
            else:
                self.inimigos_mortos += 1
                drops = self.combate_atual.gerar_drops()
                msgs = []
                for tipo, valor in drops:
                    if tipo == "ouro":
                        self.player.ouro += valor
                        msgs.append(f"{valor} Ouro")
                    else:
                        cat_item, dados_item = self.lookup_item_data(valor)
                        if dados_item:
                            sucesso = self.player.inventario.adicionar_item(valor, cat_item, dados_item)
                            if sucesso: msgs.append(f"Drop: {valor}")
                            else: msgs.append(f"Inv. Cheio: {valor}")
                        else: msgs.append(f"Item desc.: {valor}")
                if msgs:
                    self.mensagem_acao = " | ".join(msgs)
                    self.mensagem_timer = 180
                self.state = GameState.PLAYING
                self.combate_atual = None
                self.sound_manager.play_music("dungeon_ambient")
                
        elif self.combate_atual and not self.combate_atual.em_menu and self.combate_atual.animacao_timer == 0:
            self.combate_atual.turno = "enemy"
            pygame.time.wait(500)
            self.combate_atual.ataque_inimigo()
            self.combate_atual.turno = "player"
            self.combate_atual.em_menu = True
            if not self.combate_atual.player.esta_vivo():
                self.state = GameState.GAME_OVER
                self.sound_manager.stop_music()

    def handle_name_input(self, event):
        if event.key == pygame.K_RETURN:
            if self.nome_input.strip():
                tempo_total = time.time() - self.tempo_inicio
                self.ranking_manager.adicionar_ranking(self.nome_input, tempo_total, self.inimigos_mortos, self.configuracoes.dificuldade)
                self.state = GameState.MENU
                self.nome_input = ""
                self.sound_manager.play_music("menu_theme")
        elif event.key == pygame.K_BACKSPACE:
            self.nome_input = self.nome_input[:-1]
        else:
            if len(self.nome_input) < 15:
                self.nome_input += event.unicode

    def render_to_screen(self):
        target_w, target_h = self.screen.get_width(), self.screen.get_height()
        scale_w = target_w / VIRTUAL_WIDTH
        scale_h = target_h / VIRTUAL_HEIGHT
        scale = min(scale_w, scale_h)
        new_w = int(VIRTUAL_WIDTH * scale)
        new_h = int(VIRTUAL_HEIGHT * scale)
        offset_x = (target_w - new_w) // 2
        offset_y = (target_h - new_h) // 2
        if self.configuracoes.brilho < 100:
            darkness = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
            darkness.fill((0, 0, 0))
            alpha = 255 * (1 - (self.configuracoes.brilho / 100.0))
            darkness.set_alpha(int(alpha))
            self.virtual_surface.blit(darkness, (0, 0))
        scaled_surf = pygame.transform.scale(self.virtual_surface, (new_w, new_h))
        self.screen.fill(BLACK)
        self.screen.blit(scaled_surf, (offset_x, offset_y))

    def draw_menu(self):
        w, h = VIRTUAL_WIDTH, VIRTUAL_HEIGHT
        if self.menu_background:
            self.virtual_surface.blit(self.menu_background, (0, 0))
            overlay = pygame.Surface((w, h))
            overlay.set_alpha(80)
            overlay.fill(BLACK)
            self.virtual_surface.blit(overlay, (0, 0))
        else: self.virtual_surface.fill((20, 15, 30))
        
        titulo_txt = "BEYOND THE DUNGEON"
        offsets = [(-3, -3), (3, -3), (-3, 3), (3, 3)]
        for ox, oy in offsets:
            sombra = self.font_large.render(titulo_txt, False, BLACK)
            rect_s = sombra.get_rect(center=(w // 2 + ox, 130 + oy))
            self.virtual_surface.blit(sombra, rect_s)
        titulo = self.font_large.render(titulo_txt, False, GOLD)
        rect_titulo = titulo.get_rect(center=(w // 2, 130))
        self.virtual_surface.blit(titulo, rect_titulo)
        
        start_y, btn_h, btn_w, gap = 320, 70, 400, 25
        for i, op in enumerate(self.menu_opcoes):
            cx, cy = w // 2, start_y + i * (btn_h + gap)
            btn_rect = pygame.Rect(0, 0, btn_w, btn_h)
            btn_rect.center = (cx, cy)
            if i == self.menu_selecionado:
                cor_bg, cor_border, cor_txt, texto = (120, 30, 30), GOLD, WHITE, f"> {op} <"
                pygame.draw.rect(self.virtual_surface, (255, 200, 0), btn_rect, 4, border_radius=10)
            else:
                cor_bg, cor_border, cor_txt, texto = (40, 40, 50), GRAY, (180, 180, 180), op
            
            pygame.draw.rect(self.virtual_surface, cor_bg, btn_rect, border_radius=10)
            pygame.draw.rect(self.virtual_surface, cor_border, btn_rect, 2, border_radius=10)
            txt_surf = self.font_medium.render(texto, False, cor_txt)
            txt_sombra = self.font_medium.render(texto, False, BLACK)
            rect_txt = txt_surf.get_rect(center=(cx, cy))
            self.virtual_surface.blit(txt_sombra, (rect_txt.x + 2, rect_txt.y + 2))
            self.virtual_surface.blit(txt_surf, rect_txt)
        if self.ranking_ui.visivel: self.ranking_ui.draw(self.virtual_surface, self.ranking_manager)

    def draw_paused(self):
        self.draw_playing()
        overlay = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill(BLACK)
        self.virtual_surface.blit(overlay, (0, 0))
        txt_paused = self.font_large.render("JOGO PAUSADO", False, GOLD)
        rect_paused = txt_paused.get_rect(center=(VIRTUAL_WIDTH//2, VIRTUAL_HEIGHT//2 - 50))
        self.virtual_surface.blit(txt_paused, rect_paused)
        txt_resume = self.font_medium.render("ESC - Voltar", False, WHITE)
        rect_resume = txt_resume.get_rect(center=(VIRTUAL_WIDTH//2, VIRTUAL_HEIGHT//2 + 20))
        self.virtual_surface.blit(txt_resume, rect_resume)
        txt_quit = self.font_medium.render("Q - Menu Principal", False, RED)
        rect_quit = txt_quit.get_rect(center=(VIRTUAL_WIDTH//2, VIRTUAL_HEIGHT//2 + 60))
        self.virtual_surface.blit(txt_quit, rect_quit)

    def draw_transition(self):
        self.virtual_surface.fill(BLACK)
        nome_atual = DUNGEONS[self.dungeon_index]["nome"]
        texto_concluido = self.font_large.render(f"{nome_atual} Concluída!", True, GREEN)
        self.virtual_surface.blit(texto_concluido, texto_concluido.get_rect(center=(VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT // 2 - 50)))
        if self.dungeon_index + 1 < len(DUNGEONS):
            prox_nome = DUNGEONS[self.dungeon_index + 1]["nome"]
            texto_prox = self.font_medium.render(f"Próxima: {prox_nome}", True, WHITE)
            self.virtual_surface.blit(texto_prox, texto_prox.get_rect(center=(VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT // 2 + 50)))
        width_bar = 400
        pygame.draw.rect(self.virtual_surface, GRAY, (VIRTUAL_WIDTH//2 - width_bar//2, VIRTUAL_HEIGHT//2 + 150, width_bar, 20))
        pct = 1 - (self.transition_timer / 180)
        pygame.draw.rect(self.virtual_surface, GOLD, (VIRTUAL_WIDTH//2 - width_bar//2, VIRTUAL_HEIGHT//2 + 150, width_bar * pct, 20))

    def draw(self):
        if self.state == GameState.MENU: self.draw_menu()
        elif self.state == GameState.PLAYING: self.draw_playing()
        elif self.state == GameState.PAUSED: self.draw_paused()
        elif self.state == GameState.COMBAT: self.combate_atual.draw(self.virtual_surface, self.font_small, self.font_medium, self.font_large)
        elif self.state == GameState.GAME_OVER: self.draw_game_over()
        elif self.state == GameState.VICTORY: self.draw_victory()
        elif self.state == GameState.TRANSITION: self.draw_transition()
        elif self.state == GameState.SETTINGS:
            self.draw_menu()
            self.tela_config.draw(self.virtual_surface)
        self.render_to_screen()
        pygame.display.flip()

    def draw_playing(self):
        d_img = pygame.transform.scale(self.dungeon_image, (DUNGEON_SIZE, DUNGEON_SIZE))
        self.virtual_surface.blit(d_img, (-self.camera_x, -self.camera_y))
        boss_screen_x = self.boss.x - self.camera_x
        boss_screen_y = self.boss.y - self.camera_y
        self.virtual_surface.blit(self.boss.sprite, (boss_screen_x, boss_screen_y))
        self.player.draw(self.virtual_surface, self.camera_x, self.camera_y)
        self.hud.draw_all(self.virtual_surface, self.player, self.dungeon_index, len(DUNGEONS), self.mensagem_acao, self.mensagem_timer)
        if self.mensagem_timer > 0: self.mensagem_timer -= 1
        self.inventario_ui.draw(self.virtual_surface)

    def draw_input_screen(self, title, color):
        self.virtual_surface.fill(BLACK)
        t = self.font_large.render(title, False, color)
        self.virtual_surface.blit(t, t.get_rect(center=(VIRTUAL_WIDTH//2, VIRTUAL_HEIGHT//2 - 100)))
        info = self.font_medium.render(f"Inimigos: {self.inimigos_mortos} | Tempo: {int(time.time() - self.tempo_inicio)}s", False, WHITE)
        self.virtual_surface.blit(info, info.get_rect(center=(VIRTUAL_WIDTH//2, VIRTUAL_HEIGHT//2)))
        prompt = self.font_small.render("Digite seu nome e aperte ENTER:", False, GRAY)
        self.virtual_surface.blit(prompt, prompt.get_rect(center=(VIRTUAL_WIDTH//2, VIRTUAL_HEIGHT//2 + 60)))
        name_surf = self.font_large.render(self.nome_input + "_", False, GOLD)
        self.virtual_surface.blit(name_surf, name_surf.get_rect(center=(VIRTUAL_WIDTH//2, VIRTUAL_HEIGHT//2 + 120)))

    def draw_game_over(self):
        self.draw_input_screen("GAME OVER", RED)

    def draw_victory(self):
        self.draw_input_screen("VITÓRIA!", GOLD)

    def run(self):
        while self.running:
            self.delta_time = self.clock.tick(FPS) / 1000.0
            eventos = pygame.event.get()
            for event in eventos:
                if event.type == pygame.QUIT: self.running = False
                elif event.type == pygame.VIDEORESIZE:
                    if not self.configuracoes.fullscreen:
                        self.configuracoes.resolucao = (event.w, event.h)
                        self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                elif event.type == pygame.KEYDOWN:
                    if self.state in [GameState.GAME_OVER, GameState.VICTORY]:
                        self.handle_name_input(event)
            keys = pygame.key.get_pressed()
            self.input_manager.update(keys)
            
            if self.state == GameState.INTRO: self.handle_menu(keys)
            elif self.state == GameState.MENU: self.handle_menu(keys)
            elif self.state == GameState.PLAYING: self.handle_playing(keys, self.delta_time)
            elif self.state == GameState.PAUSED: self.handle_paused(keys)
            elif self.state == GameState.COMBAT: self.handle_combat(keys)
            elif self.state == GameState.TRANSITION: self.handle_transition(keys)
            elif self.state == GameState.SETTINGS: self.handle_settings(keys)
            
            if self.combate_atual and self.combate_atual.animacao_timer > 0:
                self.combate_atual.animacao_timer -= 1
            self.draw()

if __name__ == "__main__":
    game = Game()
    game.run()
