package org.aquamarine5.brainspark.exp11;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.Date;

@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
public abstract class GeometricObject {
    private String color="white";
    private boolean filled;
    private final Date dateCreated=new Date();

    @Override
    public String toString() {
        return "GeometricObject{" +
                "color='" + color + '\'' +
                ", filled=" + filled +
                ", dateCreated=" + dateCreated +
                '}';
    }

    public abstract double getArea();
    public abstract double getPerimeter();
}
