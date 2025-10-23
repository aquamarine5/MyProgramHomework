package org.aquamarine5.brainspark.exp10;

import lombok.*;

import java.util.Date;

@Getter
@NoArgsConstructor
@AllArgsConstructor
public class Loan {
    private final Date loanDate = new Date();
    @Setter
    private double annualInterestRate = 2.5;
    @Setter
    private int numberOfYears = 1;
    @Setter
    private double loanAmount = 1000;

    public double getMonthlyPayment() {
        double monthlyInterestRate = annualInterestRate / 1200;
        return loanAmount * monthlyInterestRate /
                (1 - 1 / Math.pow(1 + monthlyInterestRate, numberOfYears * 12));
    }
    public double getTotalPayment() {
        return getMonthlyPayment() * numberOfYears * 12;
    }
}
