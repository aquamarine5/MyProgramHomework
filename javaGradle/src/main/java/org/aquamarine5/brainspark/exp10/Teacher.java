package org.aquamarine5.brainspark.exp10;


public class Teacher extends Person{
    public String teacherID;
    public Teacher(String name,int age,String id){
        super(name,age);
        this.teacherID=id;
    }

    public void getInfo(){
        System.out.println("Name: " + name + ", Age: " + age + ", Teacher ID: " + teacherID);
    }
}
