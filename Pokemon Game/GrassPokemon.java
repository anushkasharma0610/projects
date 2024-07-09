import java.util.List;
public class GrassPokemon extends Pokemon {
    public GrassPokemon(String name, int health, int attack, int defence, int specialAttack, int specialDefence, int speed, int level, boolean isWild, List<Move> moves) {
        super(name, "Grass", health, attack, defence, specialAttack, specialDefence, speed, level, isWild, moves);
    }
    @Override
    public List<Move> getMoves() {
        return this.moves; // Assuming 'moves' is an attribute in the Pokemon superclass
    }
}