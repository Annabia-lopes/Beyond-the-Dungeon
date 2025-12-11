import pygame
import os

# Cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GOLD = (255, 215, 0)

class Configuracoes:
    """Gerencia as configurações do jogo"""
    def __init__(self):
        self.music_volume = 50
        self.sfx_volume = 70  
        self.resolucao = (1280, 720)
        self.fullscreen = False
        self.dificuldade = "Normal"
        self.musica_ativada = True
        self.efeitos_ativados = True
        self.brilho = 100
        
        self.dificuldades = ["Fácil", "Normal", "Difícil"]
        self.resolucoes = [(1280, 720), (1920, 1080), (800, 600)]
    
    def aumentar_music_volume(self):
        self.music_volume = min(100, self.music_volume + 10)
    
    def diminuir_music_volume(self):
        self.music_volume = max(0, self.music_volume - 10)

    def aumentar_sfx_volume(self):
        self.sfx_volume = min(100, self.sfx_volume + 10)
    
    def diminuir_sfx_volume(self):
        self.sfx_volume = max(0, self.sfx_volume - 10)
    
    def aumentar_brilho(self):
        self.brilho = min(100, self.brilho + 10)
    
    def diminuir_brilho(self):
        self.brilho = max(50, self.brilho - 10)
    
    def mudar_dificuldade(self):
        idx = self.dificuldades.index(self.dificuldade)
        self.dificuldade = self.dificuldades[(idx + 1) % len(self.dificuldades)]
    
    def mudar_resolucao(self):
        try:
            idx = self.resolucoes.index(self.resolucao)
        except ValueError:
            idx = 0
        self.resolucao = self.resolucoes[(idx + 1) % len(self.resolucoes)]
        
    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
    
    def toggle_musica(self):
        self.musica_ativada = not self.musica_ativada
    
    def toggle_efeitos(self):
        self.efeitos_ativados = not self.efeitos_ativados
    
    def obter_multiplicador_dificuldade(self):
        if self.dificuldade == "Fácil": return 0.7
        elif self.dificuldade == "Normal": return 1.0
        else: return 1.3

class TelaConfiguracao:
    """Interface de configurações com controle por setas"""
    def __init__(self, screen_width, screen_height, configuracoes):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.configuracoes = configuracoes
        self.visivel = False
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(base_dir, "assets", "BoldPixels.ttf")
        
        if os.path.exists(font_path):
            self.font_large = pygame.font.Font(font_path, 48)
            self.font_medium = pygame.font.Font(font_path, 32)
            self.font_small = pygame.font.Font(font_path, 24)
        else:
            self.font_large = pygame.font.Font(None, 48)
            self.font_medium = pygame.font.Font(None, 36)
            self.font_small = pygame.font.Font(None, 28)
        
        self.opcoes = [
            "Volume Música",
            "Volume Efeitos",
            "Brilho",
            "Dificuldade",
            "Música",
            "Efeitos Sonoros",
            "Resolução",
            "Tela Cheia",
            "Voltar"
        ]
        self.selecionado = 0
    
    def handle_input(self, keys, input_manager=None):
        if not self.visivel: return None
        
        mudanca_visual = False

        if input_manager:
            if input_manager.is_key_pressed(pygame.K_UP):
                self.selecionado = (self.selecionado - 1) % len(self.opcoes)
            
            if input_manager.is_key_pressed(pygame.K_DOWN):
                self.selecionado = (self.selecionado + 1) % len(self.opcoes)
            
            if input_manager.is_key_pressed(pygame.K_LEFT):
                if self.executar_acao_esquerda(): mudanca_visual = True
            
            if input_manager.is_key_pressed(pygame.K_RIGHT):
                if self.executar_acao_direita(): mudanca_visual = True
            
            if input_manager.is_key_pressed(pygame.K_ESCAPE):
                self.visivel = False
                return "voltar"
            
            if input_manager.is_key_pressed(pygame.K_RETURN) and self.selecionado == len(self.opcoes) - 1:
                self.visivel = False
                return "voltar"
                
        return "aplicar" if mudanca_visual else None
    
    def executar_acao_esquerda(self):
        opcao = self.opcoes[self.selecionado]
        
        if opcao == "Volume Música": self.configuracoes.diminuir_music_volume()
        elif opcao == "Volume Efeitos": self.configuracoes.diminuir_sfx_volume()
        elif opcao == "Brilho": self.configuracoes.diminuir_brilho()
        elif opcao == "Dificuldade": self.configuracoes.mudar_dificuldade()
        elif opcao == "Música": self.configuracoes.toggle_musica()
        elif opcao == "Efeitos Sonoros": self.configuracoes.toggle_efeitos()
        
        elif opcao == "Resolução": 
            try:
                idx = self.configuracoes.resolucoes.index(self.configuracoes.resolucao)
            except ValueError:
                idx = 0
            
            novo_idx = (idx - 1) % len(self.configuracoes.resolucoes)
            self.configuracoes.resolucao = self.configuracoes.resolucoes[novo_idx]
            return True
            
        elif opcao == "Tela Cheia":
            self.configuracoes.toggle_fullscreen()
            return True
            
        return False
    
    def executar_acao_direita(self):
        opcao = self.opcoes[self.selecionado]
        
        if opcao == "Volume Música": self.configuracoes.aumentar_music_volume()
        elif opcao == "Volume Efeitos": self.configuracoes.aumentar_sfx_volume()
        elif opcao == "Brilho": self.configuracoes.aumentar_brilho()
        elif opcao == "Dificuldade": self.configuracoes.mudar_dificuldade()
        elif opcao == "Música": self.configuracoes.toggle_musica()
        elif opcao == "Efeitos Sonoros": self.configuracoes.toggle_efeitos()
        
        elif opcao == "Resolução": 
            try:
                idx = self.configuracoes.resolucoes.index(self.configuracoes.resolucao)
            except ValueError:
                idx = 0
            
            novo_idx = (idx + 1) % len(self.configuracoes.resolucoes)
            self.configuracoes.resolucao = self.configuracoes.resolucoes[novo_idx]
            return True
            
        elif opcao == "Tela Cheia":
            self.configuracoes.toggle_fullscreen()
            return True
            
        return False
    
    def draw(self, screen):
        if not self.visivel: return
        
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        painel_largura = 700
        painel_altura = 650
        painel_x = (screen.get_width() - painel_largura) // 2
        painel_y = (screen.get_height() - painel_altura) // 2
        
        pygame.draw.rect(screen, (30, 30, 35), (painel_x, painel_y, painel_largura, painel_altura), border_radius=15)
        pygame.draw.rect(screen, GOLD, (painel_x, painel_y, painel_largura, painel_altura), 3, border_radius=15)
        
        titulo = self.font_large.render("CONFIGURAÇÕES", True, GOLD)
        rect_titulo = titulo.get_rect(center=(screen.get_width()//2, painel_y + 50))
        screen.blit(titulo, rect_titulo)
        
        opcoes_y = painel_y + 120
        for i, opcao in enumerate(self.opcoes):
            cor = YELLOW if i == self.selecionado else WHITE
            
            texto_opcao = self.font_medium.render(opcao, True, cor)
            screen.blit(texto_opcao, (painel_x + 60, opcoes_y + i * 50))
            
            valor = self.obter_valor_opcao(opcao)
            texto_valor = self.font_small.render(valor, True, cor)
            
            rect_valor = texto_valor.get_rect(midright=(painel_x + painel_largura - 60, opcoes_y + i * 50 + 15))
            screen.blit(texto_valor, rect_valor)
           
            if i == self.selecionado:
                pygame.draw.rect(screen, cor, (painel_x + 40, opcoes_y + i * 50 + 10, 10, 10))
        
        instrucoes = self.font_small.render("Setas para Mudar | ENTER/ESC Voltar", True, GRAY)
        rect_instr = instrucoes.get_rect(center=(screen.get_width()//2, painel_y + painel_altura - 40))
        screen.blit(instrucoes, rect_instr)
    
    def obter_valor_opcao(self, opcao):
        if opcao == "Volume Música": return f"{self.configuracoes.music_volume}%"
        elif opcao == "Volume Efeitos": return f"{self.configuracoes.sfx_volume}%"
        elif opcao == "Brilho": return f"{self.configuracoes.brilho}%"
        elif opcao == "Dificuldade": return self.configuracoes.dificuldade
        elif opcao == "Música": return "Sim" if self.configuracoes.musica_ativada else "Não"
        elif opcao == "Efeitos Sonoros": return "Sim" if self.configuracoes.efeitos_ativados else "Não"
        elif opcao == "Resolução": return f"{self.configuracoes.resolucao[0]}x{self.configuracoes.resolucao[1]}"
        elif opcao == "Tela Cheia": return "Sim" if self.configuracoes.fullscreen else "Não"
        elif opcao == "Voltar": return ""
        return ""