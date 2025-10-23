package org.aquamarine5.brainspark.exp7;

public class Main {
    public static void main(String[] args) {
        final int NUMBER_OF_STUDENTS = 100;
        boolean[] lockers=new boolean[NUMBER_OF_STUDENTS];
        for(int student=1;student<=NUMBER_OF_STUDENTS;student++){
            for(int locker=student-1;locker<NUMBER_OF_STUDENTS;locker+=student){
                lockers[locker]=!lockers[locker];
            }
        }
        for(int i=0;i<lockers.length;i++){
            if(lockers[i]){
                System.out.printf("Locker %d is open\n",i);
            }
        }
    }
}
