import pickle
import os
import pygame
from datetime import datetime


class RankingManager:
    
    def __init__(self, filename="ranking.dat"):
        self.filename = filename
        self.rankings = []
        self.load_rankings()
    
    def load_rankings(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'rb') as f:
                    self.rankings = pickle.load(f)
            except Exception as e:
                print(f"Erro ao carregar rankings: {e}")
                self.rankings = []
        else:
            self.rankings = []
    
    def save_rankings(self):
        try:
            with open(self.filename, 'wb') as f:
                pickle.dump(self.rankings, f)
        except Exception as e:
            print(f"Erro ao salvar rankings: {e}")
    
    def calcular_pontuacao(self, tempo_segundos, inimigos_mortos, dificuldade="Normal"):
        multiplicadores = {"Fácil": 0.5, "Normal": 1.0, "Difícil": 1.5}
        mult = multiplicadores.get(dificuldade, 1.0)
        pontos_inimigos = inimigos_mortos * 100
        penalidade_tempo = (tempo_segundos / 10) * mult
        pontuacao = max(0, pontos_inimigos - penalidade_tempo)
        return int(pontuacao)
    
    def adicionar_ranking(self, nome_jogador, tempo_segundos, inimigos_mortos, dificuldade="Normal"):
        pontuacao = self.calcular_pontuacao(tempo_segundos, inimigos_mortos, dificuldade)
        minutos = int(tempo_segundos // 60)
        segundos = int(tempo_segundos % 60)
        tempo_formatado = f"{minutos:02d}:{segundos:02d}"
        
        novo_ranking = {
            "nome": nome_jogador,
            "pontuacao": pontuacao,
            "tempo": tempo_formatado,
            "tempo_segundos": tempo_segundos,
            "inimigos_mortos": inimigos_mortos,
            "dificuldade": dificuldade,
            "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }
        
        self.rankings.append(novo_ranking)
        self.rankings.sort(key=lambda x: x["pontuacao"], reverse=True)
        self.rankings = self.rankings[:10]
        self.save_rankings()
        return novo_ranking
    
    def obter_top_10(self):
        return self.rankings[:10]
    
    def limpar_rankings(self):
        self.rankings = []
        self.save_rankings()


class RankingUI:
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.visivel = False
        
        self.BLACK = (0, 0, 0)
        self.WHITE = (240, 240, 240)
        self.GRAY = (128, 128, 128)
        self.DARK_GRAY = (64, 64, 64)
        
        self.GOLD = (255, 215, 0)
        self.DARK_GOLD = (184, 134, 11)
        self.SILVER = (211, 211, 211)
        self.BRONZE = (205, 127, 50)
        self.RED = (255, 80, 80)
        self.GREEN = (80, 255, 80)
       
        self.PANEL_BG = (30, 30, 35)
        self.ROW_BG_1 = (55, 55, 60)
        self.ROW_BG_2 = (45, 45, 50)
        
        self.font_loaded = False
        self.font_large = None
        self.font_medium = None
        self.font_small = None
        self.font_bold = None

    def carregar_fontes(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(base_dir, "assets", "BoldPixels.ttf")
        
        if os.path.exists(font_path):
            self.font_large = pygame.font.Font(font_path, 60)
            self.font_medium = pygame.font.Font(font_path, 32)
            self.font_small = pygame.font.Font(font_path, 26)
            self.font_bold = pygame.font.Font(font_path, 28)
        else:
            self.font_large = pygame.font.Font(None, 60)
            self.font_medium = pygame.font.Font(None, 32)
            self.font_small = pygame.font.Font(None, 26)
            self.font_bold = pygame.font.Font(None, 28)
        self.font_loaded = True
    
    def draw(self, screen, ranking_manager):
        if not self.visivel: return
        if not self.font_loaded: self.carregar_fontes()
        
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(220)
        overlay.fill(self.BLACK)
        screen.blit(overlay, (0, 0))
        
        panel_width = 950
        panel_height = 650
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = (self.screen_height - panel_height) // 2
        
        pygame.draw.rect(screen, self.PANEL_BG, (panel_x, panel_y, panel_width, panel_height), border_radius=15)
        pygame.draw.rect(screen, self.GOLD, (panel_x, panel_y, panel_width, panel_height), 4, border_radius=15)
        pygame.draw.rect(screen, self.DARK_GOLD, (panel_x+4, panel_y+4, panel_width-8, panel_height-8), 2, border_radius=12)
        
        titulo_txt = "HALL DA FAMA"
        titulo_sombra = self.font_large.render(titulo_txt, False, self.BLACK)
        titulo = self.font_large.render(titulo_txt, False, self.GOLD)
        titulo_rect = titulo.get_rect(center=(self.screen_width // 2, panel_y + 45))
        
        screen.blit(titulo_sombra, (titulo_rect.x + 3, titulo_rect.y + 3))
        screen.blit(titulo, titulo_rect)
        
        header_y = panel_y + 100
        header_height = 40
        pygame.draw.rect(screen, self.GOLD, (panel_x + 20, header_y, panel_width - 40, header_height), border_top_left_radius=8, border_top_right_radius=8)
        pygame.draw.line(screen, self.DARK_GOLD, (panel_x + 20, header_y + header_height), (panel_x + panel_width - 20, header_y + header_height), 3)
        
        col_x = [panel_x + 40, panel_x + 120, panel_x + 350, panel_x + 500, panel_x + 630, panel_x + 780]
        headers = ["Pos", "Nome", "Pontos", "Tempo", "Inimigos", "Dificuldade"]
        
        for header, x_pos in zip(headers, col_x):
            texto = self.font_bold.render(header.upper(), False, self.BLACK)
            text_rect = texto.get_rect(midleft=(x_pos, header_y + header_height // 2))
            screen.blit(texto, text_rect)
        
        rankings = ranking_manager.obter_top_10()
        row_height = 45
        row_y_start = header_y + header_height + 8
        
        for i, ranking in enumerate(rankings):
            current_row_y = row_y_start + i * (row_height + 4)
            row_rect = pygame.Rect(panel_x + 20, current_row_y, panel_width - 40, row_height)
            
            if i == 0:   
                bg_color, txt_color, border_color = self.DARK_GOLD, self.BLACK, self.GOLD
            elif i == 1: 
                bg_color, txt_color, border_color = self.SILVER, self.BLACK, self.WHITE
            elif i == 2: 
                bg_color, txt_color, border_color = self.BRONZE, self.BLACK, (255, 200, 150)
            else:        
                bg_color = self.ROW_BG_1 if i % 2 == 0 else self.ROW_BG_2
                txt_color = self.WHITE
                border_color = None

            pygame.draw.rect(screen, bg_color, row_rect, border_radius=6)
            if border_color: pygame.draw.rect(screen, border_color, row_rect, 2, border_radius=6)
            
            def draw_cell(text, x, color=txt_color):
                if color == self.WHITE:
                    sombra = self.font_small.render(str(text), False, self.BLACK)
                    rect_s = sombra.get_rect(midleft=(x+1, current_row_y + row_height // 2 + 1))
                    screen.blit(sombra, rect_s)
                surf = self.font_small.render(str(text), False, color)
                rect = surf.get_rect(midleft=(x, current_row_y + row_height // 2))
                screen.blit(surf, rect)

            pos_prefix = "1 " if i==0 else "2 " if i==1 else "3 " if i==2 else f"{i+1} "
            draw_cell(pos_prefix, col_x[0])
            draw_cell(ranking["nome"][:16], col_x[1])
            pts_color = txt_color if i < 3 else self.GOLD
            draw_cell(f"{ranking['pontuacao']:,}".replace(",", "."), col_x[2], color=pts_color)
            draw_cell(ranking["tempo"], col_x[3])
            draw_cell(f"{ranking['inimigos_mortos']}", col_x[4])
            
            dif_cores = {"Fácil": self.GREEN, "Normal": self.GOLD, "Difícil": self.RED}
            dif_cor = dif_cores.get(ranking["dificuldade"], txt_color)
            final_dif_cor = self.BLACK if i < 3 else dif_cor 
            draw_cell(ranking["dificuldade"], col_x[5], color=final_dif_cor)

        if not rankings:
            msg = self.font_medium.render("Nenhum registro. Jogue para entrar no Ranking!", False, self.GRAY)
            msg_rect = msg.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 40))
            screen.blit(msg, msg_rect)
        
        footer_y = panel_y + panel_height - 35
        pygame.draw.line(screen, self.DARK_GOLD, (panel_x + 50, footer_y - 10), (panel_x + panel_width - 50, footer_y - 10), 1)
        instr = self.font_small.render("Pressione ESC para voltar ao Menu", False, self.GRAY)
        instr_rect = instr.get_rect(center=(self.screen_width // 2, footer_y + 10))
        screen.blit(instr, instr_rect)
    
    def handle_input(self, keys):
        if keys[pygame.K_ESCAPE]:
            self.visivel = False
            return True
        return False