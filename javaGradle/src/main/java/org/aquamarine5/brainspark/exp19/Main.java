package org.aquamarine5.brainspark.exp19;

import java.io.*;
import java.util.Date;

public class Main {
    public static void main(String[] args) {
        Student student = new Student();
        try (FileOutputStream fos = new FileOutputStream("student.dat");
             ObjectOutputStream oos = new ObjectOutputStream(fos)) {
            oos.writeObject(student);
        } catch (IOException e) {
            e.printStackTrace();
        }

        Student diskStudent = null;
        try (var fis = new FileInputStream("student.dat");
             var ois = new ObjectInputStream(fis)) {
            diskStudent =
                    (Student) ois.readObject();
        } catch (IOException | ClassNotFoundException e) {
            e.printStackTrace();
        }finally {
            if (diskStudent != null) {
                System.out.println(diskStudent);
            }
        }
        System.out.println("程序运行时间："+new Date());
    }
}
