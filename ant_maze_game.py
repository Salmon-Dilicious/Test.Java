"""
螞蟻迷宮感知逃脫 — Ant Maze Perception Escape
Python / Pygame 獨立執行版本
原始網頁版作者：未知 | Python 移植版
"""
import pygame
import sys
import math
import random
from collections import deque

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════
TILE_SIZE = 60
CANVAS_SIZE = 800
FPS = 60

DIFF_CONFIG = {
    'easy':   {'size': 25, 'vision': 4, 'food_needed': 5,  'enemies': 2, 'speed': 800, 'food_spawns': 5,  'items': 3},
    'normal': {'size': 35, 'vision': 4, 'food_needed': 10, 'enemies': 4, 'speed': 500, 'food_spawns': 10, 'items': 3},
    'hard':   {'size': 45, 'vision': 2, 'food_needed': 20, 'enemies': 6, 'speed': 300, 'food_spawns': 20, 'items': 2},
}

# Colors
WALL_COLOR = (61, 43, 31)
FLOOR_COLOR = (139, 115, 85)
BG_COLOR = (17, 17, 17)
HUD_BG = (0, 0, 0, 180)
GOLD = (255, 204, 0)
WHITE = (255, 255, 255)
LIGHT_GRAY = (200, 200, 200)
MID_GRAY = (136, 136, 136)
GREEN = (76, 175, 80)
RED = (244, 67, 54)
PURPLE = (153, 0, 255)
ORANGE = (255, 136, 0)

# ═══════════════════════════════════════════════════════════════
# MAZE GENERATION (Recursive Backtracking)
# ═══════════════════════════════════════════════════════════════
def generate_maze(w, h):
    """Generate a maze using recursive backtracking."""
    maze = [[1 for _ in range(w)] for _ in range(h)]
    stack = [(1, 1)]
    maze[1][1] = 0
    dirs = [(0, -2), (0, 2), (-2, 0), (2, 0)]

    while stack:
        cx, cy = stack[-1]
        unvisited = []
        for dx, dy in dirs:
            nx, ny = cx + dx, cy + dy
            if 0 < nx < w - 1 and 0 < ny < h - 1 and maze[ny][nx] == 1:
                unvisited.append((nx, ny, dx // 2, dy // 2))

        if unvisited:
            nx, ny, wx, wy = random.choice(unvisited)
            maze[cy + wy][cx + wx] = 0
            maze[ny][nx] = 0
            stack.append((nx, ny))
        else:
            stack.pop()
    return maze

def validate_maze(maze, w, h):
    """Validate the maze has intersections and escape routes."""
    start_x, start_y = 1, 1
    queue = deque([(start_x, start_y, 0)])
    visited = {(start_x, start_y)}
    dirs = [(0, -1), (0, 1), (-1, 0), (1, 0)]

    nearest_intersection = float('inf')
    escape_at_5 = 0

    while queue:
        cx, cy, dist = queue.popleft()
        valid_moves = 0
        for dx, dy in dirs:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < w and 0 <= ny < h and maze[ny][nx] == 0:
                valid_moves += 1
        if valid_moves > 2 and dist < nearest_intersection:
            nearest_intersection = dist
        if dist == 5:
            escape_at_5 += 1
        for dx, dy in dirs:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < w and 0 <= ny < h and maze[ny][nx] == 0 and (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append((nx, ny, dist + 1))

    return nearest_intersection <= 8 and escape_at_5 >= 2

def generate_and_validate_maze(w, h):
    """Generate a valid maze. Force-fix if too many attempts fail."""
    for _ in range(50):
        maze = generate_maze(w, h)
        if validate_maze(maze, w, h):
            return maze
    # Force-create an intersection
    if w > 5 and h > 5:
        maze[1][2] = 0; maze[1][3] = 0
        maze[2][1] = 0; maze[3][1] = 0
        maze[2][3] = 0; maze[3][3] = 0
    return maze

# ═══════════════════════════════════════════════════════════════
# BFS PATHFINDING
# ═══════════════════════════════════════════════════════════════
def bfs_next_step(maze, w, h, sx, sy, tx, ty):
    """BFS shortest path. Returns the first step from (sx,sy)."""
    if sx == tx and sy == ty:
        return None
    queue = deque([(sx, sy)])
    parent = {(sx, sy): None}
    dirs = [(0, -1), (0, 1), (-1, 0), (1, 0)]

    while queue:
        cx, cy = queue.popleft()
        if cx == tx and cy == ty:
            # Trace back to first step
            step = (cx, cy)
            prev = parent[step]
            while prev is not None:
                pp = parent.get(prev)
                if pp is None:
                    return step
                step = prev
                prev = pp
            return step
        for dx, dy in dirs:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < w and 0 <= ny < h and maze[ny][nx] == 0:
                key = (nx, ny)
                if key not in parent:
                    parent[key] = (cx, cy)
                    queue.append(key)
    return None

# ═══════════════════════════════════════════════════════════════
# GAME CLASS
# ═══════════════════════════════════════════════════════════════
class AntMazeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((CANVAS_SIZE, CANVAS_SIZE))
        pygame.display.set_caption("螞蟻迷宮感知逃脫")
        self.clock = pygame.time.Clock()
        self.running = True
        self.font_large = None
        self.font_medium = None
        self.font_small = None
        self.font_emoji = None
        self._init_fonts()
        self.state = 'MENU'  # MENU, PLAYING, WIN, LOSE
        self.diff = 'easy'
        self.maze = None
        self.maze_w = 0
        self.maze_h = 0
        self.run_id = 0
        self.player = None
        self.enemies = None
        self.foods = None
        self.items = None
        self.sugar_cubes = None
        self.food_collected = 0
        self.food_needed = 0
        self.sunlight_end_time = 0
        self.slash_effect = None
        # Menu
        self.menu_options = ['easy', 'normal', 'hard']
        self.menu_selected = 0
        self.difficulty_names = {'easy': '簡單 (Easy)', 'normal': '普通 (Normal)', 'hard': '困難 (Hard)'}

    def _init_fonts(self):
        """Initialize fonts with fallbacks."""
        try:
            CJK_FONTS = 'microsoftjhenghei,microsoftjhengheiuilight,msgothic,simhei,notosanscjk'
            self.font_large = pygame.font.SysFont(CJK_FONTS, 48)
            self.font_medium = pygame.font.SysFont(CJK_FONTS, 36)
            self.font_small = pygame.font.SysFont(CJK_FONTS, 20)
            self.font_tiny = pygame.font.SysFont(CJK_FONTS, 16)
            self.font_emoji = pygame.font.SysFont('segoeuiemoji,segoesuisymbol,notoemoji', TILE_SIZE * 7 // 10)
        except Exception:
            self.font_large = pygame.font.Font(None, 48)
            self.font_medium = pygame.font.Font(None, 36)
            self.font_small = pygame.font.Font(None, 20)
            self.font_tiny = pygame.font.Font(None, 16)
            self.font_emoji = pygame.font.Font(None, TILE_SIZE * 7 // 10)

    # ── Helpers ──────────────────────────────────────────────
    def _get_config(self):
        return DIFF_CONFIG[self.diff]

    def _random_empty_pos(self, min_dist=0):
        """Get a random empty position on the maze."""
        for _ in range(1000):
            x = random.randrange(self.maze_w)
            y = random.randrange(self.maze_h)
            if self.maze[y][x] == 1:
                continue
            if x == 1 and y == 1:
                continue
            if min_dist and abs(x - self.player['x']) + abs(y - self.player['y']) < min_dist:
                continue
            return {'x': x, 'y': y}
        return {'x': 1, 'y': 1}

    def _valid_enemy_spawn(self, respawn=False):
        """Get a valid enemy spawn position."""
        cfg = self._get_config()
        for _ in range(1000):
            x = random.randrange(self.maze_w)
            y = random.randrange(self.maze_h)
            if self.maze[y][x] == 1:
                continue
            if abs(x - 1) + abs(y - 1) <= 10:
                continue
            if respawn:
                d = abs(x - self.player['x']) + abs(y - self.player['y'])
                if d <= 8 or d <= cfg['vision']:
                    continue
            return {'x': x, 'y': y}
        return {'x': 1, 'y': 1}

    def _has_line_of_sight(self, x0, y0, x1, y1):
        """Bresenham-based line of sight check."""
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        cx, cy = x0, y0
        while True:
            if self.maze[cy][cx] == 1:
                return False
            if cx == x1 and cy == y1:
                return True
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                cx += sx
            if e2 < dx:
                err += dx
                cy += sy

    def _patrol_step(self, enemy):
        """Get a patrol movement step."""
        dirs = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        valid = []
        for dx, dy in dirs:
            nx, ny = enemy['x'] + dx, enemy['y'] + dy
            if 0 <= nx < self.maze_w and 0 <= ny < self.maze_h and self.maze[ny][nx] == 0:
                valid.append((nx, ny))
        if not valid:
            return {'x': enemy['x'], 'y': enemy['y']}
        # Prefer forward (don't go back to previous tile)
        forward = [m for m in valid if m != (enemy.get('px'), enemy.get('py'))]
        if forward:
            nx, ny = random.choice(forward)
        else:
            nx, ny = random.choice(valid)
        enemy['px'] = enemy['x']
        enemy['py'] = enemy['y']
        return {'x': nx, 'y': ny}

    # ── Game Start ──────────────────────────────────────────
    def start_game(self, diff):
        self.diff = diff
        self.run_id += 1
        cfg = self._get_config()
        self.state = 'PLAYING'

        # Generate maze
        self.maze = generate_and_validate_maze(cfg['size'], cfg['size'])
        self.maze_w = len(self.maze[0])
        self.maze_h = len(self.maze)

        # Player
        self.player = {'x': 1, 'y': 1, 'dx': 0, 'dy': 1, 'inv': {'sunlight': 0, 'sword': 0, 'sugar': 0}}
        self.food_collected = 0
        self.food_needed = cfg['food_needed']
        self.sunlight_end_time = 0
        self.slash_effect = None

        # Food spawns
        self.foods = [self._random_empty_pos(5) for _ in range(cfg['food_spawns'])]

        # Items
        self.items = []
        for _ in range(cfg['items']):
            self.items.append({**self._random_empty_pos(5), 'type': 'sunlight'})
        for _ in range(cfg['items']):
            self.items.append({**self._random_empty_pos(5), 'type': 'sword'})
        for _ in range(cfg['items']):
            self.items.append({**self._random_empty_pos(5), 'type': 'sugar'})

        # Enemies
        self.enemies = []
        for _ in range(cfg['enemies']):
            pos = self._valid_enemy_spawn(False)
            self.enemies.append({
                'x': pos['x'], 'y': pos['y'],
                'px': pos['x'], 'py': pos['y'],
                'state': 'PATROL', 'last_known': None,
                'search_end': 0, 'last_move': pygame.time.get_ticks()
            })

        self.sugar_cubes = []

    # ── Collisions ──────────────────────────────────────────
    def check_collisions(self):
        px, py = self.player['x'], self.player['y']

        # Food
        for i in range(len(self.foods) - 1, -1, -1):
            if self.foods[i]['x'] == px and self.foods[i]['y'] == py:
                self.foods.pop(i)
                self.food_collected += 1
                if self.food_collected >= self.food_needed:
                    self.state = 'WIN'

        # Items
        for i in range(len(self.items) - 1, -1, -1):
            if self.items[i]['x'] == px and self.items[i]['y'] == py:
                typ = self.items[i]['type']
                self.player['inv'][typ] += 1
                self.items.pop(i)

        # Enemy collision
        for e in self.enemies:
            if e['x'] == px and e['y'] == py:
                self.state = 'LOSE'

    # ── Sword ───────────────────────────────────────────────
    def use_sword(self):
        px, py = self.player['x'], self.player['y']
        dx, dy = self.player['dx'], self.player['dy']
        hit_tiles = []
        for i in range(1, 6):
            tx, ty = px + dx * i, py + dy * i
            if tx < 0 or tx >= self.maze_w or ty < 0 or ty >= self.maze_h or self.maze[ty][tx] == 1:
                break
            hit_tiles.append((tx, ty))

        self.slash_effect = {'tiles': hit_tiles, 'expires': pygame.time.get_ticks() + 200}
        current_run = self.run_id

        for i in range(len(self.enemies) - 1, -1, -1):
            e = self.enemies[i]
            if (e['x'], e['y']) in hit_tiles:
                self.enemies.pop(i)
                # Schedule respawn after 5 seconds
                if not hasattr(self, '_pending_respawns'):
                    self._pending_respawns = []
                self._pending_respawns.append({'run_id': current_run, 'time': pygame.time.get_ticks() + 5000})

    # ── Update ──────────────────────────────────────────────
    def update(self):
        now = pygame.time.get_ticks()
        cfg = self._get_config()

        # Cleanup sugar cubes
        self.sugar_cubes = [s for s in self.sugar_cubes if s['expires'] > now]

        # Handle pending respawns
        if hasattr(self, '_pending_respawns'):
            remaining = []
            for r in self._pending_respawns:
                if r['run_id'] == self.run_id and now >= r['time']:
                    pos = self._valid_enemy_spawn(True)
                    self.enemies.append({
                        'x': pos['x'], 'y': pos['y'],
                        'px': pos['x'], 'py': pos['y'],
                        'state': 'PATROL', 'last_known': None,
                        'search_end': 0, 'last_move': now
                    })
                else:
                    remaining.append(r)
            self._pending_respawns = remaining

        # Move enemies
        for e in self.enemies:
            if now - e['last_move'] < cfg['speed']:
                continue
            e['last_move'] = now

            # Check sugar attraction first
            target_sugar = None
            min_sugar_dist = float('inf')
            for s in self.sugar_cubes:
                d = abs(s['x'] - e['x']) + abs(s['y'] - e['y'])
                if d <= 10 and d < min_sugar_dist:
                    min_sugar_dist = d
                    target_sugar = s

            if target_sugar:
                e['state'] = 'CHASE'
                step = bfs_next_step(self.maze, self.maze_w, self.maze_h,
                                     e['x'], e['y'], target_sugar['x'], target_sugar['y'])
                if step:
                    e['px'], e['py'] = e['x'], e['y']
                    e['x'], e['y'] = step
                continue

            # State transitions
            dist_to_player = abs(e['x'] - self.player['x']) + abs(e['y'] - self.player['y'])
            can_see = dist_to_player <= 6 and self._has_line_of_sight(e['x'], e['y'],
                                                                      self.player['x'], self.player['y'])

            if can_see:
                e['state'] = 'CHASE'
                e['last_known'] = {'x': self.player['x'], 'y': self.player['y']}
            elif e['state'] == 'CHASE':
                e['state'] = 'SEARCH'
                e['search_end'] = now + 5000

            if e['state'] == 'SEARCH':
                if (now > e['search_end'] or
                    (e['last_known'] and e['x'] == e['last_known']['x'] and e['y'] == e['last_known']['y'])):
                    e['state'] = 'PATROL'
                    e['last_known'] = None

            # Actions
            if e['state'] == 'PATROL':
                step = self._patrol_step(e)
                e['x'], e['y'] = step['x'], step['y']
            elif e['state'] == 'CHASE':
                step = bfs_next_step(self.maze, self.maze_w, self.maze_h,
                                     e['x'], e['y'], self.player['x'], self.player['y'])
                if step:
                    e['px'], e['py'] = e['x'], e['y']
                    e['x'], e['y'] = step
            elif e['state'] == 'SEARCH' and e['last_known']:
                step = bfs_next_step(self.maze, self.maze_w, self.maze_h,
                                     e['x'], e['y'], e['last_known']['x'], e['last_known']['y'])
                if step:
                    e['px'], e['py'] = e['x'], e['y']
                    e['x'], e['y'] = step
                else:
                    step = self._patrol_step(e)
                    e['x'], e['y'] = step['x'], step['y']

        if self.state == 'PLAYING':
            self.check_collisions()

    # ── Ray Casting (16-ray perception) ──────────────────────
    def cast_ray(self, start_x, start_y, angle_deg):
        """Cast a perception ray. Returns hit info for closest enemy and food."""
        angle_rad = math.radians(angle_deg)
        ray_dx = math.cos(angle_rad)
        ray_dy = math.sin(angle_rad)
        half_fan = math.radians(22.5)

        closest_enemy = None
        closest_enemy_dist = float('inf')
        closest_food = None
        closest_food_dist = float('inf')

        # Check enemies
        for e in self.enemies:
            ex = (e['x'] + 0.5) - start_x
            ey = (e['y'] + 0.5) - start_y
            dist = math.hypot(ex, ey)
            if dist < 0.5 or dist > 30:
                continue
            dot = ex * ray_dx + ey * ray_dy
            cross = ex * ray_dy - ey * ray_dx
            angle_between = math.atan2(abs(cross), dot)
            if angle_between <= half_fan and dist < closest_enemy_dist:
                closest_enemy_dist = dist
                closest_enemy = e

        # Check food
        for f in self.foods:
            fx = (f['x'] + 0.5) - start_x
            fy = (f['y'] + 0.5) - start_y
            dist = math.hypot(fx, fy)
            if dist < 0.5 or dist > 30:
                continue
            dot = fx * ray_dx + fy * ray_dy
            cross = fx * ray_dy - fy * ray_dx
            angle_between = math.atan2(abs(cross), dot)
            if angle_between <= half_fan and dist < closest_food_dist:
                closest_food_dist = dist
                closest_food = f

        result = {'hit_enemy': False, 'hit_food': False, 'dist': float('inf')}
        if closest_enemy and closest_food:
            if closest_enemy_dist <= closest_food_dist:
                result['hit_enemy'] = True
                result['dist'] = closest_enemy_dist
            else:
                result['hit_food'] = True
                result['dist'] = closest_food_dist
        elif closest_enemy:
            result['hit_enemy'] = True
            result['dist'] = closest_enemy_dist
        elif closest_food:
            result['hit_food'] = True
            result['dist'] = closest_food_dist
        return result

    # ── Emoji rendering helper ─────────────────────────────
    def _draw_emoji_at(self, emoji, tx, ty, cam_x, cam_y, bg_color=None, bg_radius=None):
        """Render emoji at tile (tx, ty) using the emoji font. Optional background circle."""
        sx = tx * TILE_SIZE - cam_x + TILE_SIZE // 2
        sy = ty * TILE_SIZE - cam_y + TILE_SIZE // 2
        if bg_color and bg_radius:
            pygame.draw.circle(self.screen, bg_color, (sx, sy), bg_radius)
        try:
            emoji_surf = self.font_emoji.render(emoji, True, WHITE)
        except Exception:
            emoji_surf = self.font_small.render(emoji, True, WHITE)
        self.screen.blit(emoji_surf,
                         (sx - emoji_surf.get_width() // 2,
                          sy - emoji_surf.get_height() // 2))

    # ── Render ──────────────────────────────────────────────
    def render(self):
        self.screen.fill(BG_COLOR)

        if self.state == 'MENU':
            self._render_menu()
        elif self.state in ('PLAYING', 'WIN', 'LOSE'):
            self._render_game()

        pygame.display.flip()

    def _render_menu(self):
        # Title
        title_surf = self.font_large.render("螞蟻迷宮感知逃脫", True, GOLD)
        title_rect = title_surf.get_rect(center=(CANVAS_SIZE // 2, 180))
        self.screen.blit(title_surf, title_rect)

        # Subtitle
        sub = self.font_small.render("扮演視力有限的螞蟻，在黑暗迷宮中尋找食物。避開蜘蛛，利用氣味感知方位！",
                                     True, MID_GRAY)
        sub_rect = sub.get_rect(center=(CANVAS_SIZE // 2, 240))
        self.screen.blit(sub, sub_rect)

        # Difficulty buttons
        y_start = 320
        for i, key in enumerate(self.menu_options):
            color = GOLD if i == self.menu_selected else WHITE
            bg_color = (61, 43, 31) if i == self.menu_selected else (40, 40, 40)
            btn_rect = pygame.Rect(CANVAS_SIZE // 2 - 150, y_start + i * 80, 300, 60)
            pygame.draw.rect(self.screen, bg_color, btn_rect, border_radius=8)
            pygame.draw.rect(self.screen, (139, 115, 85), btn_rect, 2, border_radius=8)
            txt = self.font_medium.render(self.difficulty_names[key], True, color)
            txt_rect = txt.get_rect(center=btn_rect.center)
            self.screen.blit(txt, txt_rect)

        # Controls info
        ctrl = self.font_tiny.render(
            "[方向鍵] 移動  |  [1] 太陽光(全視野5秒)  |  [2] 劍(攻擊前方)  |  [3] 糖塊(吸引敵人)",
            True, MID_GRAY)
        ctrl_rect = ctrl.get_rect(center=(CANVAS_SIZE // 2, 680))
        self.screen.blit(ctrl, ctrl_rect)

        ctrl2 = self.font_tiny.render("↑↓ 選擇難度  ENTER 開始遊戲", True, MID_GRAY)
        ctrl2_rect = ctrl2.get_rect(center=(CANVAS_SIZE // 2, 710))
        self.screen.blit(ctrl2, ctrl2_rect)

    def _render_game(self):
        cfg = self._get_config()
        now = pygame.time.get_ticks()

        # Camera
        cam_x = self.player['x'] * TILE_SIZE + TILE_SIZE // 2 - CANVAS_SIZE // 2
        cam_y = self.player['y'] * TILE_SIZE + TILE_SIZE // 2 - CANVAS_SIZE // 2

        # Draw maze (only visible area)
        for y in range(self.maze_h):
            for x in range(self.maze_w):
                wx = x * TILE_SIZE - cam_x
                wy = y * TILE_SIZE - cam_y
                if (wx < -TILE_SIZE or wx > CANVAS_SIZE + TILE_SIZE or
                    wy < -TILE_SIZE or wy > CANVAS_SIZE + TILE_SIZE):
                    continue
                color = WALL_COLOR if self.maze[y][x] == 1 else FLOOR_COLOR
                pygame.draw.rect(self.screen, color, (wx, wy, TILE_SIZE, TILE_SIZE))

        # Draw foods 🍎
        for f in self.foods:
            self._draw_emoji_at('🍎', f['x'], f['y'], cam_x, cam_y,
                                bg_color=(0, 60, 0, 100), bg_radius=TILE_SIZE * 0.25)

        # Draw sugar cubes 🍬 (active on ground)
        for s in self.sugar_cubes:
            self._draw_emoji_at('🍬', s['x'], s['y'], cam_x, cam_y,
                                bg_color=(80, 0, 40, 100), bg_radius=TILE_SIZE * 0.25)

        # Draw items ☀️ ⚔️ 🍬 (pickups on map)
        for item in self.items:
            emoji_map = {'sunlight': '☀️', 'sword': '⚔️', 'sugar': '🍬'}
            emoji = emoji_map.get(item['type'], '❓')
            self._draw_emoji_at(emoji, item['x'], item['y'], cam_x, cam_y,
                                bg_color=(40, 40, 40, 120), bg_radius=TILE_SIZE * 0.28)

        # Draw enemies 🕷️
        for e in self.enemies:
            self._draw_emoji_at('🕷️', e['x'], e['y'], cam_x, cam_y,
                                bg_color=(60, 0, 60, 100), bg_radius=TILE_SIZE * 0.28)

        # Draw player 🐜 (with rotation)
        px = self.player['x'] * TILE_SIZE - cam_x + TILE_SIZE // 2
        py = self.player['y'] * TILE_SIZE - cam_y + TILE_SIZE // 2
        angle = 0
        if self.player['dx'] == 1:
            angle = 90
        elif self.player['dx'] == -1:
            angle = -90
        elif self.player['dy'] == 1:
            angle = 180
        try:
            ant_surf = self.font_emoji.render('🐜', True, WHITE)
            ant_surf = pygame.transform.rotate(ant_surf, angle)
        except Exception:
            ant_surf = self.font_small.render('V', True, GOLD)
        self.screen.blit(ant_surf,
                         (px - ant_surf.get_width() // 2,
                          py - ant_surf.get_height() // 2))

        # Draw slash effect
        if self.slash_effect and self.slash_effect['expires'] > now:
            for tx, ty in self.slash_effect['tiles']:
                sx = tx * TILE_SIZE - cam_x + TILE_SIZE // 2
                sy = ty * TILE_SIZE - cam_y + TILE_SIZE // 2
                pygame.draw.circle(self.screen, (255, 255, 255, 200), (sx, sy), TILE_SIZE // 2)
                pygame.draw.circle(self.screen, (255, 255, 200), (sx, sy), TILE_SIZE // 3)

        # ── Fog of War ──
        sunlight_active = self.sunlight_end_time > now
        if not sunlight_active:
            vision = cfg['vision']
            fog = pygame.Surface((CANVAS_SIZE, CANVAS_SIZE), pygame.SRCALPHA)
            fog.fill((0, 0, 0, 200))
            # Player screen position
            psx = CANVAS_SIZE // 2
            psy = CANVAS_SIZE // 2
            inner_r = TILE_SIZE * (vision - 1)
            outer_r = TILE_SIZE * (vision + 1)

            # Cut transparent vision circle
            pygame.draw.circle(fog, (0, 0, 0, 0), (psx, psy), max(inner_r, 10))
            # Gradient edge
            for i in range(1, 6):
                r = inner_r + (outer_r - inner_r) * i // 5
                alpha = min(200, 30 * i)
                pygame.draw.circle(fog, (0, 0, 0, alpha), (psx, psy), r, width=max(2, (outer_r - inner_r) // 5))
            self.screen.blit(fog, (0, 0))

        # ── 16-Ray Perception Bars ──
        danger_flash = (now // 300) % 2 == 0
        base_angles = [0, 90, 180, 270]  # Right, Down, Left, Up
        ray_offsets = [-16.875, -5.625, 5.625, 16.875]
        segment_size = 80
        start_offset = (CANVAS_SIZE - segment_size * 4) // 2

        def draw_segment(side, idx, color, alpha=1.0):
            pos = start_offset + idx * segment_size
            if side == 0:  # Right
                rect = pygame.Rect(CANVAS_SIZE - 20, pos, 20, segment_size - 4)
            elif side == 1:  # Bottom
                rect = pygame.Rect(CANVAS_SIZE - pos - segment_size + 4, CANVAS_SIZE - 20, segment_size - 4, 20)
            elif side == 2:  # Left
                rect = pygame.Rect(0, CANVAS_SIZE - pos - segment_size + 4, 20, segment_size - 4)
            else:  # Top
                rect = pygame.Rect(pos + 4, 0, segment_size - 4, 20)
            s = pygame.Surface(rect.size, pygame.SRCALPHA)
            s.fill((*color, int(255 * alpha)))
            self.screen.blit(s, rect)

        # Phase 1: dim base segments
        for side in range(4):
            for ray in range(4):
                draw_segment(side, ray, (68, 68, 68), alpha=0.3)

        # Phase 2: ray-cast detection overlay
        for side in range(4):
            for ray in range(4):
                angle = base_angles[side] + ray_offsets[ray]
                result = self.cast_ray(self.player['x'] + 0.5, self.player['y'] + 0.5, angle)

                color = None
                if result['hit_enemy'] and result['dist'] <= 8 and danger_flash:
                    color = PURPLE
                elif result['hit_food']:
                    if result['dist'] > 15:
                        color = GREEN
                    elif result['dist'] >= 8:
                        color = ORANGE
                    else:
                        color = RED

                if color:
                    draw_segment(side, ray, color, alpha=0.8)

        # ── HUD ──
        # Top bar
        hud_top = pygame.Surface((CANVAS_SIZE, 50), pygame.SRCALPHA)
        hud_top.fill((0, 0, 0, 180))
        self.screen.blit(hud_top, (0, 0))

        food_text = f"食物: {self.food_collected} / {self.food_needed}"
        food_surf = self.font_small.render(food_text, True, WHITE)
        self.screen.blit(food_surf, (30, 14))

        # Draw HUD inventory with small emoji icons rendered separately
        inv_items = [
            ('☀️', self.player['inv']['sunlight']),
            ('⚔️', self.player['inv']['sword']),
            ('🍬', self.player['inv']['sugar']),
        ]
        x_pos = CANVAS_SIZE - 30
        for emoji_char, count in reversed(inv_items):
            try:
                icon_surf = self.font_emoji.render(emoji_char, True, WHITE)
            except Exception:
                icon_surf = self.font_small.render(emoji_char, True, WHITE)
            count_text = str(count)
            count_surf = self.font_small.render(count_text, True, WHITE)
            total_w = icon_surf.get_width() + count_surf.get_width() + 6
            x_pos -= total_w
            self.screen.blit(icon_surf, (x_pos, 25 - icon_surf.get_height() // 2))
            self.screen.blit(count_surf, (x_pos + icon_surf.get_width() + 6, 14))
            x_pos -= 16  # spacing between items

        # Bottom bar
        hud_bot = pygame.Surface((CANVAS_SIZE, 40), pygame.SRCALPHA)
        hud_bot.fill((0, 0, 0, 180))
        self.screen.blit(hud_bot, (0, CANVAS_SIZE - 40))

        ctrl_text = "方向鍵:移動 | 1:太陽光 | 2:劍 | 3:糖塊"
        ctrl_surf = self.font_tiny.render(ctrl_text, True, MID_GRAY)
        ctrl_rect = ctrl_surf.get_rect(center=(CANVAS_SIZE // 2, CANVAS_SIZE - 20))
        self.screen.blit(ctrl_surf, ctrl_rect)

        # Sunlight timer bar (if active)
        if sunlight_active:
            remaining = (self.sunlight_end_time - now) / 5000
            bar_w = int(200 * remaining)
            pygame.draw.rect(self.screen, GOLD, (CANVAS_SIZE // 2 - 100, 4, bar_w, 6), border_radius=3)
            lbl = self.font_tiny.render(f"太陽光 {int(remaining * 5)}s", True, GOLD)
            lbl_rect = lbl.get_rect(center=(CANVAS_SIZE // 2, 16))
            self.screen.blit(lbl, lbl_rect)

        # ── Win / Lose overlay ──
        if self.state == 'WIN':
            overlay = pygame.Surface((CANVAS_SIZE, CANVAS_SIZE), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            self.screen.blit(overlay, (0, 0))
            win_text = self.font_large.render("你贏了！", True, GREEN)
            win_rect = win_text.get_rect(center=(CANVAS_SIZE // 2, CANVAS_SIZE // 2 - 40))
            self.screen.blit(win_text, win_rect)
            sub = self.font_small.render(f"收集了所有食物！({self.food_collected}/{self.food_needed})", True, WHITE)
            sub_rect = sub.get_rect(center=(CANVAS_SIZE // 2, CANVAS_SIZE // 2 + 20))
            self.screen.blit(sub, sub_rect)
            hint = self.font_tiny.render("按 ENTER 返回主選單", True, MID_GRAY)
            hint_rect = hint.get_rect(center=(CANVAS_SIZE // 2, CANVAS_SIZE // 2 + 70))
            self.screen.blit(hint, hint_rect)

        elif self.state == 'LOSE':
            overlay = pygame.Surface((CANVAS_SIZE, CANVAS_SIZE), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            self.screen.blit(overlay, (0, 0))
            lose_text = self.font_large.render("遊戲結束", True, RED)
            lose_rect = lose_text.get_rect(center=(CANVAS_SIZE // 2, CANVAS_SIZE // 2 - 40))
            self.screen.blit(lose_text, lose_rect)
            sub = self.font_small.render("你被蜘蛛抓到了...", True, WHITE)
            sub_rect = sub.get_rect(center=(CANVAS_SIZE // 2, CANVAS_SIZE // 2 + 20))
            self.screen.blit(sub, sub_rect)
            hint = self.font_tiny.render("按 ENTER 返回主選單", True, MID_GRAY)
            hint_rect = hint.get_rect(center=(CANVAS_SIZE // 2, CANVAS_SIZE // 2 + 70))
            self.screen.blit(hint, hint_rect)

    # ── Input ───────────────────────────────────────────────
    def handle_input(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            return

        if event.type == pygame.KEYDOWN:
            if self.state == 'MENU':
                if event.key == pygame.K_UP:
                    self.menu_selected = (self.menu_selected - 1) % len(self.menu_options)
                elif event.key == pygame.K_DOWN:
                    self.menu_selected = (self.menu_selected + 1) % len(self.menu_options)
                elif event.key == pygame.K_RETURN:
                    self.start_game(self.menu_options[self.menu_selected])
                return

            # WIN / LOSE: ENTER returns to menu
            if self.state in ('WIN', 'LOSE'):
                if event.key == pygame.K_RETURN:
                    self.state = 'MENU'
                return

            # PLAYING
            if self.state != 'PLAYING':
                return

            px, py = self.player['x'], self.player['y']
            moved = False
            if event.key == pygame.K_UP:
                py -= 1; self.player['dx'] = 0; self.player['dy'] = -1; moved = True
            elif event.key == pygame.K_DOWN:
                py += 1; self.player['dx'] = 0; self.player['dy'] = 1; moved = True
            elif event.key == pygame.K_LEFT:
                px -= 1; self.player['dx'] = -1; self.player['dy'] = 0; moved = True
            elif event.key == pygame.K_RIGHT:
                px += 1; self.player['dx'] = 1; self.player['dy'] = 0; moved = True

            if moved:
                if 0 <= px < self.maze_w and 0 <= py < self.maze_h and self.maze[py][px] == 0:
                    self.player['x'] = px
                    self.player['y'] = py
                    self.check_collisions()

            # Item usage
            if event.key == pygame.K_1 and self.player['inv']['sunlight'] > 0:
                self.player['inv']['sunlight'] -= 1
                self.sunlight_end_time = pygame.time.get_ticks() + 5000
            elif event.key == pygame.K_2 and self.player['inv']['sword'] > 0:
                self.player['inv']['sword'] -= 1
                self.use_sword()
            elif event.key == pygame.K_3 and self.player['inv']['sugar'] > 0:
                self.player['inv']['sugar'] -= 1
                self.sugar_cubes.append({
                    'x': self.player['x'], 'y': self.player['y'],
                    'expires': pygame.time.get_ticks() + 10000
                })

    # ── Main Loop ───────────────────────────────────────────
    def run(self):
        while self.running:
            for event in pygame.event.get():
                self.handle_input(event)

            if self.state == 'PLAYING':
                self.update()

            self.render()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


# ═══════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════
if __name__ == '__main__':
    game = AntMazeGame()
    game.run()
