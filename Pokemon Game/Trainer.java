import java.util.List;

public class Trainer {
    private String name;
    private List<Pokemon> team;
    private List<Item> inventory;

    public Trainer(String name, List<Pokemon> team, List<Item> inventory) {
        this.name = name;
        this.team = team;
        this.inventory = inventory;
    }

    public List<Pokemon> getTeam() {
        return team;
    }

    public void catchPokemon(Pokemon wildPokemon, Item pokeball) {
        if (pokeball.getType().equals("pokeball")) {
            double catchRate = calculateCatchRate(wildPokemon, pokeball);
            if (Math.random() < catchRate) { // Randomness used here
                team.add(wildPokemon);
                System.out.println(name + " caught " + wildPokemon.getName() + "!");
            } else {
                System.out.println("The wild " + wildPokemon.getName() + " broke free!");
            }
        }
    }

    public void useItem(Item item, Pokemon target) {
        item.use(target);
        inventory.remove(item);
    }

    public void battle(Trainer opponent) {
        // Simplified turn-based battle
        while (!team.isEmpty() && !opponent.team.isEmpty()) {
            Pokemon myPokemon = team.get(0);
            Pokemon opponentPokemon = opponent.team.get(0);
            if (myPokemon.isFainted()) {
                team.remove(0);
                continue;
            }
            if (opponentPokemon.isFainted()) {
                opponent.team.remove(0);
                continue;
            }

            myPokemon.attack(opponentPokemon, myPokemon.moves.get(0)); // Simplified attack
            if (!opponentPokemon.isFainted()) {
                opponentPokemon.attack(myPokemon, opponentPokemon.moves.get(0)); // Simplified attack
            }
        }
        System.out.println("Battle ended!");
    }

    private double calculateCatchRate(Pokemon wildPokemon, Item pokeball) {
        // Simplified catch rate calculation
        return 0.5;
    }
}
