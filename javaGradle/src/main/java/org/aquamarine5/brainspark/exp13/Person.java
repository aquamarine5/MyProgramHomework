package org.aquamarine5.brainspark.exp13;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.Setter;

@AllArgsConstructor
@Setter
@Getter
public class Person extends Object{
    private String name;
    protected int money;

    public void earnMoney(int amount) {
        this.money += amount;
    }

    protected final void spendMoney(int amount){
        this.money -= amount;
    }

    public static int getBasicMoney(){
        return 100;
    }
}
