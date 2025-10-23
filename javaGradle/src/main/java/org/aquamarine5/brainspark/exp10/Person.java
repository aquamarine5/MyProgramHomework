package org.aquamarine5.brainspark.exp10;

import lombok.AllArgsConstructor;

@AllArgsConstructor
public class Person {
    public String name;
    public int age;

    public void getInfo(){
        System.out.println("Name: " + name + ", Age: " + age);
    }
}
