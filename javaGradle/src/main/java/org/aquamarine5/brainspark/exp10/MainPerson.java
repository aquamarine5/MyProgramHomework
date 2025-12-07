package org.aquamarine5.brainspark.exp10;

public class MainPerson {
    public static void main(String[] args) {
        A b = new B();
        b.m(5);
        System.out.println(b.i);
    }
}

class A {
    int i = 1;

    public void m(int i) {
        this.i = i;
    }
}

class B extends A {
    // int i = 4;
    int j = 2;

    public void m(int i) {
        this.i = i;
    }
}
