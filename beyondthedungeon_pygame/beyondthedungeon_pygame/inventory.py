import pygame
import os

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (40, 40, 40)
MID_GRAY = (60, 60, 60)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 50, 200)
YELLOW = (255, 255, 0)
GOLD = (218, 165, 32)

class Item:
    def __init__(self, nome, tipo, dados):
        self.nome = nome
        self.tipo = tipo
        self.dados = dados
        self.quantidade = 1
        self.sprite = self.carregar_sprite()

    def carregar_sprite(self):
        if "sprite" in self.dados:
            path = self.dados["sprite"]
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    return pygame.transform.scale(img, (32, 32))
                except: pass
        surf = pygame.Surface((32, 32))
        cor = RED if self.tipo == 'arma' else BLUE if self.tipo == 'armadura' else GREEN
        surf.fill(cor)
        return surf

class Inventario:
    def __init__(self, capacidade=30):
        self.itens = []
        self.capacidade = capacidade
    
    def adicionar_item(self, nome, tipo, dados):
        if len(self.itens) < self.capacidade:
            self.itens.append(Item(nome, tipo, dados))
            return True
        return False
    
    def remover_item(self, indice):
        if 0 <= indice < len(self.itens):
            self.itens.pop(indice)
            return True
        return False

class InventarioUI:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.visivel = False
        self.largura = 800
        self.altura = 500
        self.x = (screen_width - self.largura) // 2
        self.y = (screen_height - self.altura) // 2
        
        self.cols = 6
        self.slot_size = 64
        self.gap = 10
        self.start_grid_x = self.x + 30
        self.start_grid_y = self.y + 100
        
        self.info_x = self.start_grid_x + (self.cols * (self.slot_size + self.gap)) + 20
        self.info_y = self.start_grid_y
        self.info_w = self.largura - (self.info_x - self.x) - 30
        self.info_h = 350

        base_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(base_dir, "assets", "BoldPixels.ttf")
        if os.path.exists(font_path):
             self.font_title = pygame.font.Font(font_path, 40)
             self.font_name = pygame.font.Font(font_path, 32)
             self.font_desc = pygame.font.Font(font_path, 20)
        else:
             self.font_title = pygame.font.Font(None, 48)
             self.font_name = pygame.font.Font(None, 36)
             self.font_desc = pygame.font.Font(None, 24)
        
        self.abas = ["Todos", "Armas", "Armaduras", "Magias", "Poções"]
        self.aba_selecionada = 0
        self.itens_aba = []
        self.item_selecionado = 0
    
    def atualizar_itens_aba(self, inventario):
        aba = self.abas[self.aba_selecionada]
        if aba == "Todos": self.itens_aba = inventario.itens
        elif aba == "Armas": self.itens_aba = [i for i in inventario.itens if i.tipo == "arma"]
        elif aba == "Armaduras": self.itens_aba = [i for i in inventario.itens if i.tipo == "armadura"]
        elif aba == "Magias": self.itens_aba = [i for i in inventario.itens if i.tipo == "magia"]
        else: self.itens_aba = [i for i in inventario.itens if i.tipo in ["pocao", "consumivel"]]
        
        if self.item_selecionado >= len(self.itens_aba):
            self.item_selecionado = max(0, len(self.itens_aba) - 1)
    
    def handle_input(self, keys, inventario, player, input_manager=None):
        if input_manager and input_manager.is_key_pressed(pygame.K_i):
            self.visivel = not self.visivel
            if self.visivel: self.atualizar_itens_aba(inventario)
            return None
        
        if not self.visivel: return None

        if input_manager:
            if input_manager.is_key_pressed(pygame.K_TAB):
                self.aba_selecionada = (self.aba_selecionada + 1) % len(self.abas)
                self.atualizar_itens_aba(inventario)
                self.item_selecionado = 0
            
            if input_manager.is_key_pressed(pygame.K_RIGHT):
                if len(self.itens_aba) > 0: self.item_selecionado = (self.item_selecionado + 1) % len(self.itens_aba)
            elif input_manager.is_key_pressed(pygame.K_LEFT):
                if len(self.itens_aba) > 0: self.item_selecionado = (self.item_selecionado - 1) % len(self.itens_aba)
            elif input_manager.is_key_pressed(pygame.K_UP):
                novo = self.item_selecionado - self.cols
                if novo >= 0: self.item_selecionado = novo
            elif input_manager.is_key_pressed(pygame.K_DOWN):
                novo = self.item_selecionado + self.cols
                if novo < len(self.itens_aba): self.item_selecionado = novo
            elif input_manager.is_key_pressed(pygame.K_RETURN):
                if self.itens_aba:
                    res = self.usar_item(self.itens_aba[self.item_selecionado], player, inventario)
                    self.atualizar_itens_aba(inventario)
                    return res
            elif input_manager.is_key_pressed(pygame.K_ESCAPE):
                self.visivel = False
                return None
        return None

    def usar_item(self, item, player, inventario):
        try: idx = inventario.itens.index(item)
        except: return None
        
        msg, consumiu = "", False
        if item.tipo == "arma":
            player.equipamentos["arma"] = item.dados
            msg = f"Equipou: {item.nome}"
        elif item.tipo == "armadura":
            player.equipamentos["armadura"] = item.dados
            msg = f"Vestiu: {item.nome}"
        elif item.tipo in ["pocao", "consumivel"]:
            d = item.dados
            if "cura" in d: player.curar(d["cura"]); msg=f"Curou {d['cura']}"; consumiu=True
            if "mana" in d: player.restaurar_mana(d["mana"]); msg=f"Mana +{d['mana']}"; consumiu=True
            if "ataque" in d: msg=f"Usou {item.nome}"; consumiu=True
            if consumiu:
                inventario.remover_item(idx)
                self.item_selecionado = min(self.item_selecionado, max(0, len(self.itens_aba) - 1))
        elif item.tipo == "magia": msg = f"Magia {item.nome} equipada."
        return msg

    def draw(self, screen):
        if not self.visivel: return
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(180); overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        rect = pygame.Rect(self.x, self.y, self.largura, self.altura)
        pygame.draw.rect(screen, DARK_GRAY, rect, border_radius=10)
        pygame.draw.rect(screen, GOLD, rect, 3, border_radius=10)
        
        screen.blit(self.font_title.render("BOLSA", False, GOLD), (self.x+30, self.y+20))
        
        ax = self.x + 30
        for i, aba in enumerate(self.abas):
            cbg = GOLD if i==self.aba_selecionada else MID_GRAY
            ctx = BLACK if i==self.aba_selecionada else WHITE
            r = pygame.Rect(ax, self.y+60, 100, 30)
            pygame.draw.rect(screen, cbg, r, border_radius=5)
            t = self.font_desc.render(aba, False, ctx)
            screen.blit(t, t.get_rect(center=r.center))
            ax += 110
            
        screen.blit(self.font_desc.render("[TAB] Trocar Aba", False, GRAY), (ax+20, self.y+68))

        for i in range(24):
            c, r = i % self.cols, i // self.cols
            sx, sy = self.start_grid_x + c*(74), self.start_grid_y + r*(74)
            pygame.draw.rect(screen, MID_GRAY, (sx, sy, 64, 64))
            pygame.draw.rect(screen, BLACK, (sx, sy, 64, 64), 1)

        for i, item in enumerate(self.itens_aba):
            if i >= 24: break
            c, r = i % self.cols, i // self.cols
            sx, sy = self.start_grid_x + c*(74), self.start_grid_y + r*(74)
            if item.sprite:
                sr = item.sprite.get_rect(center=(sx+32, sy+32))
                if sr.w < 33:
                    sc = pygame.transform.scale(item.sprite, (48, 48))
                    screen.blit(sc, sc.get_rect(center=(sx+32, sy+32)))
                else: screen.blit(item.sprite, sr)
            if i == self.item_selecionado:
                pygame.draw.rect(screen, WHITE, (sx, sy, 64, 64), 3)

        pygame.draw.rect(screen, (30,30,30), (self.info_x, self.info_y, self.info_w, self.info_h), border_radius=5)
        pygame.draw.rect(screen, GOLD, (self.info_x, self.info_y, self.info_w, self.info_h), 2, border_radius=5)
        
        if self.itens_aba and len(self.itens_aba) > 0:
            sel = self.itens_aba[self.item_selecionado]
            screen.blit(self.font_name.render(sel.nome, False, GOLD), (self.info_x+15, self.info_y+15))
            screen.blit(self.font_desc.render(f"Tipo: {sel.tipo}", False, GRAY), (self.info_x+15, self.info_y+50))
            pygame.draw.line(screen, GRAY, (self.info_x+10, self.info_y+80), (self.info_x+self.info_w-10, self.info_y+80))
            
            sy = self.info_y + 90
            for k, v in sel.dados.items():
                if k == "sprite": continue
                ck = WHITE
                if k in ["ataque", "dano"]: ck = RED
                elif k in ["defesa"]: ck = BLUE
                elif k in ["cura"]: ck = GREEN
                screen.blit(self.font_desc.render(f"{k.capitalize()}: {v}", False, ck), (self.info_x+15, sy))
                sy += 30
            
            if sel.sprite:
                li = pygame.transform.scale(sel.sprite, (128, 128))
                img_x = self.info_x + (self.info_w // 2) - 64
                img_y = self.info_y + self.info_h - 140 
                
                bg_rect = pygame.Rect(img_x-10, img_y-10, 148, 148)
                pygame.draw.rect(screen, (20, 20, 20), bg_rect, border_radius=10)
                pygame.draw.rect(screen, GOLD, bg_rect, 2, border_radius=10)
                
                screen.blit(li, (img_x, img_y))
        else:
            screen.blit(self.font_desc.render("Vazio", False, GRAY), (self.info_x+20, self.info_y+50))
            
        screen.blit(self.font_desc.render("[Setas] Navegar | [ENTER] Usar | [I] Fechar", False, WHITE), (self.x+200, self.y+470))