package org.aquamarine5.brainspark.exp12;

public class Employee extends Person{
    public Employee(String name) {
        super(name);
    }

    @Override
    public String toString() {
        return "Employee{" +
                "name='" + getName() + "'}";
    }
}
