package org.aquamarine5.brainspark.exp16;

public class Chicken extends Animal implements Edible{
    @Override
    public String sound() {
        return "Chicken: cock-a-doodle-doo";
    }

    @Override
    public String howToEat() {
        return "Chicken: Fry it";
    }
}
