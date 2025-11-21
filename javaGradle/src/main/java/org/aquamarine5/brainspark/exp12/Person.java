package org.aquamarine5.brainspark.exp12;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.Setter;

@AllArgsConstructor
@Getter
@Setter
public class Person {
    private String name;

    @Override
    public String toString() {
        return "Person{" +
                "name='" + name + "'}";
    }
}
