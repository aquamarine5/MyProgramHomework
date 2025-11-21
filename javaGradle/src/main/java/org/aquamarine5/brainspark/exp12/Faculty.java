package org.aquamarine5.brainspark.exp12;

public class Faculty extends Employee{
    public Faculty(String name) {
        super(name);
    }

    public String toString() {
        return "Faculty(Employee){" +
                "name='" + getName() + "'}";
    }
}
