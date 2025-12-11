import pygame
from PIL import Image

class CollisionMap:
    
    def __init__(self, image_path, dungeon_size=1280):
        self.dungeon_size = dungeon_size
        self.collision_data = None
        self.load_collision_map(image_path)
    
    def load_collision_map(self, image_path):
        try:
            img = Image.open(image_path).convert('RGB')
            
            if img.size != (self.dungeon_size, self.dungeon_size):
                img = img.resize((self.dungeon_size, self.dungeon_size), Image.Resampling.LANCZOS)
            
            pixels = img.load()
            
            self.collision_data = {}
            for y in range(self.dungeon_size):
                for x in range(self.dungeon_size):
                    r, g, b = pixels[x, y]
                    is_black = (r < 10 and g < 10 and b < 10)
                    self.collision_data[(x, y)] = not is_black
            
            print(f"✓ Mapa de colisão carregado: {image_path}")
        except Exception as e:
            print(f"✗ Erro ao carregar mapa de colisão: {e}")
            self.collision_data = {(x, y): True for x in range(self.dungeon_size) for y in range(self.dungeon_size)}
    
    def is_passable(self, x, y, width=48, height=48):
        if not self.collision_data:
            return True
        
        check_points = [
            (x, y),                          
            (x + width - 1, y),             
            (x, y + height - 1),            
            (x + width - 1, y + height - 1), 
            (x + width // 2, y),             
            (x + width // 2, y + height - 1), 
            (x, y + height // 2),           
            (x + width - 1, y + height // 2),
        ]
        
        for px, py in check_points:
            px = max(0, min(px, self.dungeon_size - 1))
            py = max(0, min(py, self.dungeon_size - 1))
            
            if not self.collision_data.get((px, py), True):
                return False
        
        return True
    
    def find_spawn_point(self):
        import random
        
        attempts = 0
        max_attempts = 1000
        
        while attempts < max_attempts:
            x = random.randint(100, self.dungeon_size - 150)
            y = random.randint(self.dungeon_size - 300, self.dungeon_size - 100)
            
            if self.is_passable(x, y):
                return (x, y)
            
            attempts += 1
        
        print("⚠ Usando posição de spawn padrão")
        return (self.dungeon_size // 2 - 24, self.dungeon_size - 150)
        
    def find_boss_spawn_point(self):
        import random
        
        attempts = 0
        max_attempts = 500
        
        while attempts < max_attempts:
            x = random.randint(100, self.dungeon_size - 150)
            y = random.randint(50, self.dungeon_size // 4)
            
            if self.is_passable(x, y):
                return (x, y)
            
            attempts += 1
        
        print("⚠ Usando posição de spawn padrão para boss")
        return (self.dungeon_size // 2 - 24, 100)