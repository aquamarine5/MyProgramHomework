package org.aquamarine5.brainspark.exp17;

public class MainStudent {
    public static void main(String[] args) {
        Student s1 = new Student("Alice", 20);
        Student s2 = new Student("Bob", 22);
        Student s3 = s1.clone();
        Student s4 = s2;
        s1.setAge(1215);
        s4.setAge(1214);
        System.out.println(s1);
        System.out.println(s2);
        System.out.println(s3);
        System.out.println(s4);
    }
}
