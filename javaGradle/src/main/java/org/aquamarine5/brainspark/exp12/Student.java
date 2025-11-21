package org.aquamarine5.brainspark.exp12;

public class Student extends Person{
    public Student(String name) {
        super(name);
    }

    @Override
    public String toString() {
        return "Student{" +
                "name='" + getName() + "'}";
    }
}
