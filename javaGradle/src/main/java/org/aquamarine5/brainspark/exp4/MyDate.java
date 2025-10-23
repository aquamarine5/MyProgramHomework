package org.aquamarine5.brainspark.exp4;

public record MyDate(int year,int month,int day){
    private static int thisYear=2000;
    static {
        thisYear=3000;
    }

    @Override
    public String toString() {
        return "%d/%d/%d".formatted(year,month,day);
    }

    public static int getThisYear(){
        return thisYear;
    }
}