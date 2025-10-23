package org.aquamarine5.brainspark.exp16;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public abstract class Animal {
    private double weight;
    public abstract String sound();
}
