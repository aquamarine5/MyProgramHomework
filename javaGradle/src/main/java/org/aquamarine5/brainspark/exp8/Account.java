package org.aquamarine5.brainspark.exp8;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.Setter;

import java.util.Date;

@AllArgsConstructor
@Getter
@Setter
public class Account {
    @Setter
    private static double annualInterestRate;
    private final Date dateCreated = new Date();
    private int id;
    private double balance;

    public double getMonthlyInterest() {
        return balance * annualInterestRate / 1200;
    }

    public void withdraw(double amount) {
        balance -= amount;
    }

    public void deposit(double amount) {
        balance += amount;
    }
}
