import java.util.List;
public abstract class Pokemon {
    protected String name;
    protected String type;
    protected int health;
    protected int maxHealth;
    protected int attack;
    protected int defence;
    protected int specialAttack;
    protected int specialDefence;
    protected int speed;
    protected int level;
    protected int experience;
    protected List<Move> moves;
    protected boolean isWild;

    public Pokemon(String name, String type, int health, int attack, int defence, int specialAttack, int specialDefence, int speed, int level, boolean isWild, List<Move> moves) {
        this.name = name;
        this.type = type;
        this.health = health;
        this.maxHealth = health;
        this.attack = attack;
        this.defence = defence;
        this.specialAttack = specialAttack;
        this.specialDefence = specialDefence;
        this.speed = speed;
        this.level = level;
        this.experience = 0;
        this.isWild = isWild;
        this.moves = moves;
    }

    public void attack(Pokemon opponent, Move move) {
        if (move.getAccuracy() > Math.random() * 100) { // Randomness used here
            int damage = calculateDamage(move, opponent);
            opponent.takeDamage(damage);
            move.applyEffect(opponent); // Apply the move's effect
            System.out.println(name + " used " + move.getName() + "!");
        } else {
            System.out.println(name + "'s attack missed!");
        }
    }

    public void takeDamage(int damage) {
        health -= damage;
        if (health <= 0) {
            health = 0;
            System.out.println(name + " fainted!");
        }
    }

    public void gainExperience(int exp) {
        experience += exp;
        if (experience >= level * 100) {
            levelUp();
        }
    }

    public void levelUp() {
        level++;
        health += 10;
        maxHealth += 10;
        attack += 2;
        defence += 2;
        specialAttack += 2;
        specialDefence += 2;
        speed += 2;
        System.out.println(name + " leveled up to level " + level + "!");
        // Check for new moves
    }

    public void learnMove(Move move) {
        if (moves.size() < 4) {
            moves.add(move);
            System.out.println(name + " learned " + move.getName() + "!");
        } else {
            System.out.println(name + " can't learn more than 4 moves!");
        }
    }

    public int getStat(String stat) {
        switch (stat.toLowerCase()) {
            case "health": return health;
            case "attack": return attack;
            case "defence": return defence;
            case "specialattack": return specialAttack;
            case "specialdefence": return specialDefence;
            case "speed": return speed;
            case "maxhealth": return maxHealth;
            default: throw new IllegalArgumentException("Invalid stat: " + stat);
        }
    }

    private int calculateDamage(Move move, Pokemon opponent) {
        int baseDamage = move.getPower();
        double typeEffectiveness = 1.0; // Calculate based on types
        return (int) (baseDamage * typeEffectiveness);
    }

    public String getName() {
        return name;
    }
    public boolean isFainted() {
        return health <= 0;
    }
    public abstract List<Move> getMoves(); // Abstract method to be implemented by subclasses

    public int getLevel() {
        return level;
    }
}

