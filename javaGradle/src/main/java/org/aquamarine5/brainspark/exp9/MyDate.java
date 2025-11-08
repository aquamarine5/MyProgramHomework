package org.aquamarine5.brainspark.exp9;

import lombok.AllArgsConstructor;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.Setter;

@Setter
@Getter
@EqualsAndHashCode
@AllArgsConstructor
public class MyDate {
    private static final int thisYear;

    static{
        thisYear=2025;
    }

    private int year = 1970;
    private int month = 1;
    private int day = 1;

    public void set(int year, int month, int day) {
        this.year = year;
        this.month = (month >= 1 && month <= 12) ? month : 1;
        this.day = (day >= 1 && day <= 31) ? day : 1;
    }

    public void set(MyDate date){
        this.year = date.year;
        this.month = date.month;
        this.day = date.day;
    }

    public String toString() {
        return String.format("%04d年%02d月%02d日", year, month, day);
    }

    public static boolean isLeapYear(int year) {
        return (year % 4 == 0 && year % 100 != 0) || (year % 400 == 0);
    }

    public boolean isLeapYear() {
        return isLeapYear(this.year);
    }

    public static int daysOfMonth(int year,int month){
        return switch (month) {
            case 1, 3, 5, 7, 8, 10, 12 -> 31;
            case 4, 6, 9, 11 -> 30;
            case 2 -> isLeapYear(year) ? 29 : 28;
            default -> 0;
        };
    }

    public int daysOfMonth(){
        return daysOfMonth(this.year,this.month);
    }

    public void tomorrow(){
        if(this.day<daysOfMonth()){
            this.day++;
        }else{
            this.day=1;
            if(this.month<12){
                this.month++;
            }else{
                this.month=1;
                this.year++;
            }
        }
    }

    public void yesterday(){
        if(this.day>1){
            this.day--;
        }else{
            if(this.month>1){
                this.month--;
            }else{
                this.month=12;
                this.year--;
            }
            this.day=daysOfMonth();
        }
    }
}
