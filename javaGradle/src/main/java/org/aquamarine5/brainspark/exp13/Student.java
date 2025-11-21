package org.aquamarine5.brainspark.exp13;

import lombok.Getter;

public class Student extends Person {
    @Getter
    private final int id;

    public Student(String name,int money, int id) {
        super(name,money);
        this.id = id;
    }

//    @Override
//    public void spendMoney(int amount) {
//        super.spendMoney(amount - 5);
//    }

    public void earnMoney(int amount) {
        var basic=getBasicMoney();
        super.earnMoney(amount + 10);
    }

    @Override
    public String toString() {
        return "Student{" +
                "name='" + getName() + "'}";
    }

}
