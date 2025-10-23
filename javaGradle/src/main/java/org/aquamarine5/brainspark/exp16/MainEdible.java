package org.aquamarine5.brainspark.exp16;

public class MainEdible {
    public static void main(String[] args){
        Object[] objects={new Tiger(),new Chicken(),new Apple()};
        for(Object obj:objects){
            if(obj instanceof Edible edible){
                System.out.println(edible.howToEat());
            }
            if(obj instanceof Animal animal){
                System.out.println(animal.sound());
            }
        }
    }
}
