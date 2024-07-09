public class Item {
    private String name;
    private String type;
    private String effect;

    public Item(String name, String type, String effect) {
        this.name = name;
        this.type = type;
        this.effect = effect;
    }

    public String getType() {
        return type;
    }

    public void use(Pokemon target) {
        // Apply effect to target
        if (type.equals("potion")) {
            target.takeDamage(-20); // Heal 20 HP
        }
    }
}
