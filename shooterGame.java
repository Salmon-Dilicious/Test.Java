import java.awt.Color;
import java.awt.Graphics;
import java.awt.event.*;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import java.util.PriorityQueue;
import java.util.Random;
import java.util.Set;
import javax.swing.*;

public class shooterGame extends JPanel implements ActionListener, KeyListener {
    private javax.swing.Timer timer;
    
    // Player 1 State
    private int playerX = 300;
    private int playerY = 450;
    private int playerHP = 100;
    private int playerSpeed = 5;
    private int p1SpeedBuffTimer = 0;
    private int p1WeaponLevel = 1;
    
    // Player 2 State
    private int player2X = 200;
    private int player2Y = 450;
    private int player2HP = 100;
    private int player2Speed = 5;
    private int p2SpeedBuffTimer = 0;
    private int p2WeaponLevel = 1;

    private ArrayList<Bullet> bullets = new ArrayList<>();
    private ArrayList<Enemy> enemies = new ArrayList<>();
    private ArrayList<Obstacle> obstacles = new ArrayList<>();
    private ArrayList<Item> items = new ArrayList<>();
    private Random random = new Random();
    private int score = 0;
    private boolean gameOver = false;
    private boolean paused = false;
    private boolean[] keys = new boolean[256];
    private final int GRID_SIZE = 25;
    private final int GRID_WIDTH = 20;
    private final int GRID_HEIGHT = 20;

    public shooterGame() {
        setFocusable(true);
        addKeyListener(this);
        timer = new Timer(20, this);
        timer.start();
        initializeObstacles();
    }

    private void initializeObstacles() {
        obstacles.add(new Obstacle(5, 5));
        obstacles.add(new Obstacle(10, 10));
        obstacles.add(new Obstacle(15, 5));
        obstacles.add(new Obstacle(5, 15));
        obstacles.add(new Obstacle(10, 15));
    }

    public void paintComponent(Graphics g) {
        super.paintComponent(g);
        g.setColor(Color.BLACK);
        g.fillRect(0, 0, 500, 500);

        // Draw obstacles
        g.setColor(Color.GRAY);
        for (Obstacle obs : obstacles) {
            g.fillRect(obs.x * GRID_SIZE, obs.y * GRID_SIZE, GRID_SIZE, GRID_SIZE);
        }

        // Draw items
        for (Item item : items) {
            if (item.type == 0) g.setColor(Color.GREEN);
            else if (item.type == 1) g.setColor(Color.CYAN);
            else if (item.type == 2) g.setColor(Color.MAGENTA);
            g.fillOval(item.x + 5, item.y + 5, 15, 15);
        }

        // Draw Player 1
        if (playerHP > 0) {
            g.setColor(Color.BLUE);
            g.fillRect(playerX, playerY, 20, 20);
        }

        // Draw Player 2
        if (player2HP > 0) {
            g.setColor(Color.GREEN);
            g.fillRect(player2X, player2Y, 20, 20);
        }

        // Draw bullets
        g.setColor(Color.YELLOW);
        for (Bullet b : bullets) {
            g.fillRect(b.x, b.y, 5, 10);
        }

        // Draw enemies
        g.setColor(Color.RED);
        for (Enemy e : enemies) {
            g.fillRect(e.x, e.y, 20, 20);
        }

        // Draw HUD
        g.setColor(Color.WHITE);
        g.drawString("Score: " + score, 10, 20);
        g.drawString("P1 HP: " + playerHP + " | WepLv: " + p1WeaponLevel, 10, 40);
        g.drawString("P2 HP: " + player2HP + " | WepLv: " + p2WeaponLevel, 10, 60);

        if (gameOver) {
            g.setColor(Color.WHITE);
            g.drawString("Game Over! Press R to Restart", 150, 250);
        }

        if (paused) {
            g.setColor(Color.WHITE);
            g.drawString("Paused! Press P to Resume", 150, 250);
        }
    }

    public void actionPerformed(ActionEvent e) {
        if (!gameOver && !paused) {
            // Speed Buff Decay
            if (p1SpeedBuffTimer > 0) {
                p1SpeedBuffTimer--;
                if (p1SpeedBuffTimer <= 0) playerSpeed = 5;
            }
            if (p2SpeedBuffTimer > 0) {
                p2SpeedBuffTimer--;
                if (p2SpeedBuffTimer <= 0) player2Speed = 5;
            }

            // Player 1 Movement
            if (playerHP > 0) {
                if (keys[KeyEvent.VK_LEFT] && canMove(playerX - playerSpeed, playerY)) playerX -= playerSpeed;
                if (keys[KeyEvent.VK_RIGHT] && canMove(playerX + playerSpeed, playerY)) playerX += playerSpeed;
                if (keys[KeyEvent.VK_UP] && canMove(playerX, playerY - playerSpeed)) playerY -= playerSpeed;
                if (keys[KeyEvent.VK_DOWN] && canMove(playerX, playerY + playerSpeed)) playerY += playerSpeed;
            }

            // Player 2 Movement
            if (player2HP > 0) {
                if (keys[KeyEvent.VK_A] && canMove(player2X - player2Speed, player2Y)) player2X -= player2Speed;
                if (keys[KeyEvent.VK_D] && canMove(player2X + player2Speed, player2Y)) player2X += player2Speed;
                if (keys[KeyEvent.VK_W] && canMove(player2X, player2Y - player2Speed)) player2Y -= player2Speed;
                if (keys[KeyEvent.VK_S] && canMove(player2X, player2Y + player2Speed)) player2Y += player2Speed;
            }

            // Move bullets
            for (int i = 0; i < bullets.size(); i++) {
                Bullet b = bullets.get(i);
                b.x += b.dx;
                b.y += b.dy;
                if (b.y < 0 || b.x < 0 || b.x > 500) {
                    bullets.remove(i);
                    i--;
                }
            }

            // Move enemies
            for (int i = 0; i < enemies.size(); i++) {
                Enemy en = enemies.get(i);
                moveEnemy(en);
                if (en.y > 500 || en.hp <= 0) {
                    enemies.remove(i);
                    i--;
                }
            }

            // Spawn enemies
            if (random.nextInt(100) < 2) {
                int spawnX = random.nextInt(GRID_WIDTH) * GRID_SIZE;
                int spawnY = 0;
                if (!isObstacle(spawnX / GRID_SIZE, spawnY / GRID_SIZE)) {
                    enemies.add(new Enemy(spawnX, spawnY));
                }
            }

            // Spawn items
            if (items.size() < 4 && random.nextInt(300) < 1) {
                int spawnX = random.nextInt(GRID_WIDTH) * GRID_SIZE;
                int spawnY = random.nextInt(GRID_HEIGHT) * GRID_SIZE;
                if (!isObstacle(spawnX / GRID_SIZE, spawnY / GRID_SIZE)) {
                    items.add(new Item(spawnX, spawnY, random.nextInt(3)));
                }
            }

            // Check item collisions
            for (int i = 0; i < items.size(); i++) {
                Item item = items.get(i);
                boolean collected = false;
                if (playerHP > 0 && playerX < item.x + GRID_SIZE && playerX + 20 > item.x && playerY < item.y + GRID_SIZE && playerY + 20 > item.y) {
                    applyItemEffect(1, item.type);
                    collected = true;
                } else if (player2HP > 0 && player2X < item.x + GRID_SIZE && player2X + 20 > item.x && player2Y < item.y + GRID_SIZE && player2Y + 20 > item.y) {
                    applyItemEffect(2, item.type);
                    collected = true;
                }
                if (collected) {
                    items.remove(i);
                    i--;
                }
            }

            // Check bullet collisions
            for (int i = 0; i < bullets.size(); i++) {
                Bullet b = bullets.get(i);
                for (int j = 0; j < enemies.size(); j++) {
                    Enemy en = enemies.get(j);
                    if (b.x < en.x + 20 && b.x + 5 > en.x && b.y < en.y + 20 && b.y + 10 > en.y) {
                        en.hp -= 50;
                        bullets.remove(i);
                        if (en.hp <= 0) {
                            enemies.remove(j);
                            score += 10;
                        }
                        i--;
                        break;
                    }
                }
            }

            // Check collisions with enemies
            for (int i = 0; i < enemies.size(); i++) {
                Enemy en = enemies.get(i);
                boolean enemyRemoved = false;
                
                if (playerHP > 0 && playerX < en.x + 20 && playerX + 20 > en.x && playerY < en.y + 20 && playerY + 20 > en.y) {
                    playerHP -= 20;
                    enemies.remove(i);
                    i--;
                    enemyRemoved = true;
                }
                
                if (!enemyRemoved && player2HP > 0 && player2X < en.x + 20 && player2X + 20 > en.x && player2Y < en.y + 20 && player2Y + 20 > en.y) {
                    player2HP -= 20;
                    enemies.remove(i);
                    i--;
                }
            }

            // Check player collisions with obstacles
            for (Obstacle obs : obstacles) {
                int obsX = obs.x * GRID_SIZE;
                int obsY = obs.y * GRID_SIZE;
                
                if (playerHP > 0 && playerX < obsX + GRID_SIZE && playerX + 20 > obsX && playerY < obsY + GRID_SIZE && playerY + 20 > obsY) {
                    playerHP -= 1; 
                }
                if (player2HP > 0 && player2X < obsX + GRID_SIZE && player2X + 20 > obsX && player2Y < obsY + GRID_SIZE && player2Y + 20 > obsY) {
                    player2HP -= 1; 
                }
            }

            if (playerHP <= 0 && player2HP <= 0) {
                gameOver = true;
            }
        }
        repaint();
    }

    private void applyItemEffect(int player, int type) {
        if (player == 1) {
            if (type == 0) playerHP = Math.min(100, playerHP + 30);
            else if (type == 1) { playerSpeed = 10; p1SpeedBuffTimer = 150; }
            else if (type == 2) p1WeaponLevel = 2;
        } else {
            if (type == 0) player2HP = Math.min(100, player2HP + 30);
            else if (type == 1) { player2Speed = 10; p2SpeedBuffTimer = 150; }
            else if (type == 2) p2WeaponLevel = 2;
        }
    }

    private void moveEnemy(Enemy en) {
        int targetX, targetY;
        
        if (playerHP > 0 && player2HP > 0) {
            int dist1 = heuristic(en.x / GRID_SIZE, en.y / GRID_SIZE, playerX / GRID_SIZE, playerY / GRID_SIZE);
            int dist2 = heuristic(en.x / GRID_SIZE, en.y / GRID_SIZE, player2X / GRID_SIZE, player2Y / GRID_SIZE);
            if (dist1 <= dist2) {
                targetX = playerX / GRID_SIZE;
                targetY = playerY / GRID_SIZE;
            } else {
                targetX = player2X / GRID_SIZE;
                targetY = player2Y / GRID_SIZE;
            }
        } else if (playerHP > 0) {
            targetX = playerX / GRID_SIZE;
            targetY = playerY / GRID_SIZE;
        } else if (player2HP > 0) {
            targetX = player2X / GRID_SIZE;
            targetY = player2Y / GRID_SIZE;
        } else {
            en.y += en.speed;
            return;
        }

        List<Node> path = findPath(en.x / GRID_SIZE, en.y / GRID_SIZE, targetX, targetY);
        
        if (path != null && path.size() > 1) {
            Node next = path.get(1);
            int nextPx = next.x * GRID_SIZE;
            int nextPy = next.y * GRID_SIZE;
            
            if (en.x < nextPx) en.x += Math.min(en.speed, nextPx - en.x);
            else if (en.x > nextPx) en.x -= Math.min(en.speed, en.x - nextPx);
            
            if (en.y < nextPy) en.y += Math.min(en.speed, nextPy - en.y);
            else if (en.y > nextPy) en.y -= Math.min(en.speed, en.y - nextPy);
        } else {
            en.y += en.speed;
        }
    }

    private List<Node> findPath(int startX, int startY, int goalX, int goalY) {
        PriorityQueue<Node> openList = new PriorityQueue<>((a, b) -> a.f - b.f);
        Set<Node> closedList = new HashSet<>();
        Node start = new Node(startX, startY, 0, heuristic(startX, startY, goalX, goalY), null);
        openList.add(start);

        while (!openList.isEmpty()) {
            Node current = openList.poll();
            if (current.x == goalX && current.y == goalY) {
                return reconstructPath(current);
            }
            closedList.add(current);

            for (int[] dir : new int[][]{{0,1},{1,0},{0,-1},{-1,0}}) {
                int nx = current.x + dir[0];
                int ny = current.y + dir[1];
                if (nx >= 0 && nx < GRID_WIDTH && ny >= 0 && ny < GRID_HEIGHT && !isObstacle(nx, ny)) {
                    Node neighbor = new Node(nx, ny, current.g + 1, heuristic(nx, ny, goalX, goalY), current);
                    if (!closedList.contains(neighbor) && !openList.contains(neighbor)) {
                        openList.add(neighbor);
                    }
                }
            }
        }
        return null;
    }

    private int heuristic(int x1, int y1, int x2, int y2) {
        return Math.abs(x1 - x2) + Math.abs(y1 - y2);
    }

    private List<Node> reconstructPath(Node current) {
        List<Node> path = new ArrayList<>();
        while (current != null) {
            path.add(0, current);
            current = current.parent;
        }
        return path;
    }

    private boolean canMove(int x, int y) {
        int gridX = x / GRID_SIZE;
        int gridY = y / GRID_SIZE;
        return gridX >= 0 && gridX < GRID_WIDTH && gridY >= 0 && gridY < GRID_HEIGHT;
    }

    private boolean isObstacle(int x, int y) {
        for (Obstacle obs : obstacles) {
            if (obs.x == x && obs.y == y) return true;
        }
        return false;
    }

    public void keyPressed(KeyEvent e) {
        keys[e.getKeyCode()] = true;
        
        // Player 1 Shoot
        if (e.getKeyCode() == KeyEvent.VK_SPACE && !gameOver && playerHP > 0) {
            if (p1WeaponLevel == 1) {
                bullets.add(new Bullet(playerX + 7, playerY, 0, -5));
            } else {
                bullets.add(new Bullet(playerX + 7, playerY, 0, -5));
                bullets.add(new Bullet(playerX + 7, playerY, -2, -5));
                bullets.add(new Bullet(playerX + 7, playerY, 2, -5));
            }
        }
        
        // Player 2 Shoot
        if (e.getKeyCode() == KeyEvent.VK_Y && !gameOver && player2HP > 0) {
            if (p2WeaponLevel == 1) {
                bullets.add(new Bullet(player2X + 7, player2Y, 0, -5));
            } else {
                bullets.add(new Bullet(player2X + 7, player2Y, 0, -5));
                bullets.add(new Bullet(player2X + 7, player2Y, -2, -5));
                bullets.add(new Bullet(player2X + 7, player2Y, 2, -5));
            }
        }
        
        // Game Controls
        if (e.getKeyCode() == KeyEvent.VK_R && gameOver) restartGame();
        if (e.getKeyCode() == KeyEvent.VK_P) paused = !paused;
    }

    public void keyReleased(KeyEvent e) {
        keys[e.getKeyCode()] = false;
    }

    public void keyTyped(KeyEvent e) {}

    private void restartGame() {
        playerX = 300; playerY = 450; playerHP = 100; playerSpeed = 5;
        p1SpeedBuffTimer = 0; p1WeaponLevel = 1;
        
        player2X = 200; player2Y = 450; player2HP = 100; player2Speed = 5;
        p2SpeedBuffTimer = 0; p2WeaponLevel = 1;
        
        bullets.clear(); enemies.clear(); items.clear();
        score = 0; gameOver = false;
    }

    public static void main(String[] args) {
        JFrame frame = new JFrame("Shooter Game");
        shooterGame game = new shooterGame();
        frame.add(game);
        frame.setSize(500, 500);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setVisible(true);
    }

    class Bullet {
        int x, y, dx, dy;
        Bullet(int x, int y, int dx, int dy) {
            this.x = x; this.y = y; this.dx = dx; this.dy = dy;
        }
    }

    class Enemy {
        int x, y, speed, hp;
        Enemy(int x, int y) {
            this.x = x; this.y = y;
            this.speed = random.nextInt(2) + 1;
            this.hp = 50;
        }
    }

    class Obstacle {
        int x, y;
        Obstacle(int x, int y) {
            this.x = x; this.y = y;
        }
    }

    class Item {
        int x, y, type;
        Item(int x, int y, int type) {
            this.x = x; this.y = y; this.type = type;
        }
    }

    class Node {
        int x, y, g, h, f;
        Node parent;
        Node(int x, int y, int g, int h, Node parent) {
            this.x = x; this.y = y; this.g = g; this.h = h; this.f = g + h;
            this.parent = parent;
        }
        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (o == null || getClass() != o.getClass()) return false;
            Node node = (Node) o;
            return x == node.x && y == node.y;
        }
        @Override
        public int hashCode() {
            return Objects.hash(x, y);
        }
    }
}