import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        // Initialize moves
        Move tackle = new Move("Tackle", "Normal", 40, 100, "physical", null);
        Move ember = new Move("Ember", "Fire", 40, 100, "special", "burn");
        Move waterGun = new Move("Water Gun", "Water", 40, 100, "special", null);
        Move vineWhip = new Move("Vine Whip", "Grass", 45, 100, "physical", null);

        // Initialize Pokemon
        List<Move> charmanderMoves = new ArrayList<>();
        charmanderMoves.add(tackle);
        charmanderMoves.add(ember);

        List<Move> squirtleMoves = new ArrayList<>();
        squirtleMoves.add(tackle);
        squirtleMoves.add(waterGun);

        Pokemon charmander = new FirePokemon("Charmander", 100, 52, 43, 60, 50, 65, 5, true, charmanderMoves);
        Pokemon squirtle = new WaterPokemon("Squirtle", 100, 48, 65, 50, 64, 43, 5, true, squirtleMoves);

        // Initialize Trainers
        List<Pokemon> playerTeam = new ArrayList<>();
        playerTeam.add(charmander);

        List<Pokemon> opponentTeam = new ArrayList<>();
        opponentTeam.add(squirtle);

        Trainer player = new Trainer("Player", playerTeam, new ArrayList<>());
        Trainer opponent = new Trainer("Opponent", opponentTeam, new ArrayList<>());

        // Game loop
        boolean gameOn = true;

        System.out.println("Welcome to the Pokémon game!");
        while (gameOn) {
            System.out.println("Choose an action: ");
            System.out.println("1. View Pokemon");
            System.out.println("2. Attack");
            System.out.println("3. Use Item");
            System.out.println("4. Battle");
            System.out.println("5. Quit");

            int choice = scanner.nextInt();

            switch (choice) {
                case 1:
                    viewPokemon(player);
                    break;
                case 2:
                    attackPokemon(player, opponent);
                    break;
                case 3:
                    useItem(player);
                    break;
                case 4:
                    player.battle(opponent);
                    break;
                case 5:
                    gameOn = false;
                    System.out.println("Thanks for playing!");
                    break;
                default:
                    System.out.println("Invalid choice. Please choose again.");
            }
        }

        scanner.close();
    }

    private static void viewPokemon(Trainer trainer) {
        System.out.println("Your Pokemon:");
        for (Pokemon p : trainer.getTeam()) {
            System.out.println(p.getName() + " - Level: " + p.getLevel() + " HP: " + p.getStat("health") + "/" + p.getStat("maxHealth"));
        }
    }

    private static void attackPokemon(Trainer player, Trainer opponent) {
        if (player.getTeam().isEmpty() || opponent.getTeam().isEmpty()) {
            System.out.println("No Pokemon to battle.");
            return;
        }
        Pokemon playerPokemon = player.getTeam().get(0);
        Pokemon opponentPokemon = opponent.getTeam().get(0);

        Scanner scanner = new Scanner(System.in);
        System.out.println("Choose a move: ");
        for (int i = 0; i < playerPokemon.getMoves().size(); i++) {
            System.out.println((i + 1) + ". " + playerPokemon.getMoves().get(i).getName());
        }

        int moveChoice = scanner.nextInt();
        if (moveChoice < 1 || moveChoice > playerPokemon.getMoves().size()) {
            System.out.println("Invalid move choice.");
            return;
        }

        playerPokemon.attack(opponentPokemon, playerPokemon.getMoves().get(moveChoice - 1));

        if (!opponentPokemon.isFainted()) {
            opponentPokemon.attack(playerPokemon, opponentPokemon.getMoves().get(0));
        }
    }

    private static void useItem(Trainer player) {
        // For simplicity, assume player has one potion
        Item potion = new Item("Potion", "potion", "Heal 20 HP");

        if (player.getTeam().isEmpty()) {
            System.out.println("No Pokemon to use items on.");
            return;
        }
        Pokemon playerPokemon = player.getTeam().get(0);

        player.useItem(potion, playerPokemon);
        System.out.println(playerPokemon.getName() + " was healed by 20 HP.");
    }
}
