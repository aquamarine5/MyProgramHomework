package org.aquamarine5.brainspark.exp19;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.Setter;

@AllArgsConstructor
@Getter
@Setter
public class Student implements java.io.Serializable {
    private String name;
    private long id;
    private String major;
    public Student() {
        this.name = "石一泽";
        this.id = 20242605031L;
        this.major = "Software Engineering";
    }

    @Override
    public String toString() {
        return "Student{" +
                "name='" + name + '\'' +
                ", id=" + id +
                ", major='" + major + '\'' +
                '}';
    }
}

