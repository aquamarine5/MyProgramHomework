#include<stdio.h>
int main(){
    char c[4];
    printf("Enter a 4-digit positive number: ");
    scanf("%s", c);
    for(int i=3; i>=0; --i){
        printf("%c",c[i]);
    }
}