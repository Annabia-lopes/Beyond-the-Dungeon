import pygame


class HUD:
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.font_tiny = pygame.font.Font("assets/BoldPixels.ttf", 18)
        self.font_small = pygame.font.Font("assets/BoldPixels.ttf", 24)
        
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GOLD = (255, 215, 0)
        self.DARK_GRAY = (64, 64, 64)
        self.GRAY = (128, 128, 128)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.YELLOW = (255, 255, 0)
    
    def draw_all(self, screen, player, dungeon_index, total_dungeons, mensagem_acao, mensagem_timer):
        
        x_pos = 15
        y_pos = 15
        
        texto_dungeon = self.font_tiny.render(f"Dungeon {dungeon_index + 1}/{total_dungeons}", True, self.GOLD)
        screen.blit(texto_dungeon, (x_pos, y_pos))
        
        vida_percent = max(0, player.vida / player.vida_max)
        cor_vida = self.GREEN if vida_percent > 0.5 else self.YELLOW if vida_percent > 0.25 else self.RED
        
        barra_width, barra_height = 120, 10
        barra_x = x_pos
        barra_y = y_pos + 25
        
        pygame.draw.rect(screen, (40, 40, 40), (barra_x, barra_y, barra_width, barra_height))
        barra_filled = int(barra_width * vida_percent)
        if barra_filled > 0:
            pygame.draw.rect(screen, cor_vida, (barra_x, barra_y, barra_filled, barra_height))
        pygame.draw.rect(screen, self.GOLD, (barra_x, barra_y, barra_width, barra_height), 1)
        
        texto_hp_label = self.font_tiny.render("HP", True, self.WHITE)
        screen.blit(texto_hp_label, (barra_x + barra_width + 8, barra_y + 1))
        
        mana_percent = max(0, player.mana / player.mana_max)
        
        barra_y_mana = barra_y + 18
        pygame.draw.rect(screen, (40, 40, 40), (barra_x, barra_y_mana, barra_width, barra_height))
        barra_mana_filled = int(barra_width * mana_percent)
        if barra_mana_filled > 0:
            pygame.draw.rect(screen, self.BLUE, (barra_x, barra_y_mana, barra_mana_filled, barra_height))
        pygame.draw.rect(screen, self.GOLD, (barra_x, barra_y_mana, barra_width, barra_height), 1)
        
        texto_mp_label = self.font_tiny.render("MP", True, self.WHITE)
        screen.blit(texto_mp_label, (barra_x + barra_width + 8, barra_y_mana + 1))
        
        texto_itens = self.font_tiny.render(f"Items: {len(player.inventario.itens)}/{player.inventario.capacidade}", True, self.YELLOW)
        screen.blit(texto_itens, (x_pos, barra_y_mana + 25))
        
        texto_atalhos = self.font_tiny.render("[I] Inv | [ESC] Menu | [R] Ranking", True, self.GRAY)
        texto_atalhos_rect = texto_atalhos.get_rect(center=(self.screen_width // 2, self.screen_height - 20))
        screen.blit(texto_atalhos, texto_atalhos_rect)
        
        if mensagem_timer > 0:
            texto_msg = self.font_small.render(mensagem_acao, True, self.GOLD)
            texto_msg_rect = texto_msg.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            screen.blit(texto_msg, texto_msg_rect)
