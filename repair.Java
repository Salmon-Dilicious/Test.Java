import java.util.Scanner;
import java.util.Random;

public class TeachingWerewolfGame {

    static class Player {
        private int id;
        private String role;
        private boolean alive;

        public Player(int id, String role) {
            this.id = id;
            this.role = role;
            this.alive = true;
        }

        public int getId() {
            return id;
        }

        public String getRole() {
            return role;
        }

        public boolean isAlive() {
            return alive;
        }

        public void death() {
            alive = false;
        }

        public void kill() {
            alive = false;
        }

        public String getPublicInfo() {
            if (alive) {
                return "Player " + id + " : [Alive]";
            } else {
                return "Player " + id + " : [Dead]";
            }
        }
    }

    public static int findAliveWereWolf(Player[] players) {
        for (int i = 0; i < players.length; i++) {
            if (players[i].getRole().equals("Werewolf") && players[i].isAlive()) {
                return i;
            }
        }
        return -1;
    }

    public static void printAlivePlayers(Player[] players) {
        for (Player p : players) {
            if (p.isAlive()) {
                System.out.println(p.getPublicInfo());
            }
        }
    }

    public static boolean isValidTarget(int targetId, Player wolf, Player[] players) {
        if (targetId < 1 || targetId > players.length) {
            return false;
        }
        Player target = players[targetId - 1];
        if (!target.isAlive()) {
            return false;
        }
        if (target.getId() == wolf.getId()) {
            return false;
        }
        return true;
    }

    public static boolean checkKillVillagerWin(Player[] players) {
        for (Player p : players) {
            if (p.getRole().equals("Werewolf") && p.isAlive()) {
                return false;
            }
        }
        return true;
    }

    public static boolean checkKillWerewolfWin(Player[] players) {
        int villager = 0;
        int wolf = 0;

        for (Player p : players) {
            if (p.isAlive()) {
                if (p.getRole().equals("Werewolf")) {
                    wolf++;
                } else {
                    villager++;
                }
            }
        }

        return wolf >= villager;
    }

    public static void main(String[] args) {

        Scanner sc = new Scanner(System.in);
        Random rand = new Random();

        System.out.println("Welcome to Wolf Gaming!");

        System.out.print("Enter number of players: ");
        int n = sc.nextInt();
        sc.nextLine();

        Player[] players = new Player[n];

        int wolfIndex = rand.nextInt(n);

        for (int i = 0; i < n; i++) {
            if (i == wolfIndex) {
                players[i] = new Player(i + 1, "Werewolf");
            } else {
                players[i] = new Player(i + 1, "Villager");
            }
        }

        System.out.println();
        System.out.println("Role assignment start");
        System.out.println("Each player take turn to check role.");

        for (int i = 0; i < n; i++) {
            System.out.println();
            System.out.println("Player " + (i + 1) + " please enter");
            sc.nextLine();

            System.out.println("Your Role : " + players[i].getRole());
            System.out.println("Memorize your role, then press enter.");
            sc.nextLine();

            for (int line = 0; line < 30; line++) {
                System.out.println();
            }
        }

        boolean gameOver = false;
        int round = 1;

        while (!gameOver) {

            System.out.println("Round " + round);
            System.out.println();

            System.out.println("Night falls. Werewolf wakes up.");

            int aliveWereWolf = findAliveWereWolf(players);

            if (aliveWereWolf != -1) {

                System.out.println("Werewolf, it's your turn.");
                System.out.println("Alive players:");

                printAlivePlayers(players);

                int targetId;

                while (true) {
                    System.out.print("Choose a player to kill: ");

                    if (sc.hasNextInt()) {
                        targetId = sc.nextInt();

                        if (isValidTarget(targetId, players[aliveWereWolf], players)) {
                            break;
                        } else {
                            System.out.println("Invalid target. Choose again.");
                        }
                    } else {
                        sc.next();
                    }
                }

                players[targetId - 1].kill();
                System.out.println("Night result: Player " + targetId + " died.");

            } else {
                System.out.println("No werewolf alive. Skipping night phase.");
            }

            if (checkKillVillagerWin(players)) {
                System.out.println("Villagers win! All werewolves have been killed.");
                gameOver = true;
            } else if (checkKillWerewolfWin(players)) {
                System.out.println("Werewolf wins! Villagers are outnumbered.");
                gameOver = true;
            }

            round++;
        }

        sc.close();
    }
}