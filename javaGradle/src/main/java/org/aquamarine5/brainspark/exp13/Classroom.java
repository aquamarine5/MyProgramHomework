package org.aquamarine5.brainspark.exp13;

import java.util.ArrayList;

public class Classroom {
    private final ArrayList<Person> people = new ArrayList<>();

    public static void main(String[] args) {
        Person p = new Student("John", 150, 1);
        Student s = new Student("Alice", 200, 2);
        Student ps = (Student) p;
        if(s instanceof Person){
            System.out.println("s is a Person");
        }
    }
}
