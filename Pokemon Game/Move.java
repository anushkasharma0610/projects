public class Move {
    private String name;
    private String type;
    private int power;
    private int accuracy;
    private String category; // "physical" or "special"
    private String effect;

    public Move(String name, String type, int power, int accuracy, String category, String effect) {
        this.name = name;
        this.type = type;
        this.power = power;
        this.accuracy = accuracy;
        this.category = category;
        this.effect = effect;
    }

    public String getName() {
        return name;
    }

    public String getType() {
        return type;
    }

    public int getPower() {
        return power;
    }

    public int getAccuracy() {
        return accuracy;
    }

    public String getCategory() {
        return category;
    }

    public void applyEffect(Pokemon target) {
        if (effect == null) return;

        switch (effect.toLowerCase()) {
            case "burn":
                // Apply burn effect: lose health over time
                target.takeDamage(10); // Example: 10 HP damage from burn
                System.out.println(target.getName() + " was burned!");
                break;
            case "poison":
                // Apply poison effect: lose health over time
                target.takeDamage(10); // Example: 10 HP damage from poison
                System.out.println(target.getName() + " was poisoned!");
                break;
            case "paralyze":
                // Apply paralyze effect: chance to skip turn
                System.out.println(target.getName() + " was paralyzed!");
                // Paralyze logic could be handled in the battle loop
                break;
            // Add more effects as needed
            default:
                System.out.println("Unknown effect: " + effect);
        }
    }
}
