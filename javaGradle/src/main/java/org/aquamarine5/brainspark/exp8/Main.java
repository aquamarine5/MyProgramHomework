package org.aquamarine5.brainspark.exp8;

public class Main {
    public static void main(String[] args){
        Account account=new Account(1122,20000);
        Account.setAnnualInterestRate(4.5);

        account.withdraw(2500);
        account.deposit(3000);

        System.out.printf("Balance is %.2f\n",account.getBalance());
        System.out.printf("Monthly interest is %.2f\n",account.getMonthlyInterest());
        System.out.println("This account was created at "+account.getDateCreated());
    }
}
