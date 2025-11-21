package org.aquamarine5.brainspark.exp12;


public class Staff extends Employee{
    public Staff(String name) {
        super(name);
    }

    @Override
    public String toString() {
        return "Staff(Employee){" +
                "name='" + getName() + "'}";
    }
}
