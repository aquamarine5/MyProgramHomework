package org.aquamarine5.brainspark.exp1;

public class Main {
    public static void main(String[] args) {
        if(args.length==0)
            System.out.println("Hello!");
        else
            for (String arg : args) System.out.println(arg);
    }
}