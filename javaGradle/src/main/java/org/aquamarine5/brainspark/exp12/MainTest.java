package org.aquamarine5.brainspark.exp12;

public class MainTest {
    public static void main(String[] args) {
        Person person = new Person("Peter");
        Student student = new Student("Susan");
        Employee employee = new Employee("Eva");
        Faculty faculty = new Faculty("Frank");
        Staff staff = new Staff("Shane");

        System.out.println(person);
        System.out.println(employee);
        System.out.println(student);
        System.out.println((Person)faculty);
        System.out.println((Employee)staff);
    }
}
