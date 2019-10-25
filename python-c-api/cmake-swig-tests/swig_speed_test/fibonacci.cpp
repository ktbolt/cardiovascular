/* file fibonacci.cpp */
#include <iostream>
#include "stdio.h"
#include "stdlib.h"
#include <cmath>

long fibonacci_recursion( long n)
{
    long a=1;
    if(n >= 2)
    {
        a = fibonacci_recursion(n-1) + fibonacci_recursion(n-2);
    }
        // prlongf( ", %d", a );
        return a;
}

long fibonacci_iteration(long n, long nmax)
{
    long a, b,i;
    a = 0;
    b = 1;
    // std::cout << a;
    // for( long i = 0; i + a <=n ; b = i ) {
    // while(a<=n){
    for(int k=0; k<n; k++){
        i = (a + b) % nmax;
        a = b;
        b = i;
// std::cout << ", " << i;
    }
    return a;
    // std::cout << std::endl;
}

long fibonacci_full_iteration( long n, long nmax)
{
    long n0 = 0;
    for(long i=0; i<n; i++)
    {
        n0+= fibonacci_iteration(i, nmax);
    }
    return n0;
}

int main( int argc, char** argv) {
    if ( argc > 3 || argc == 1 ) {
        printf("argc: %d\n", argc);
        printf("Fibonacci takes one postitive integer greater\
                than two as it's argument\n");
        return EXIT_SUCCESS;
    }

    long n = atof( argv[1] );
    long nmax_exp = atof( argv[2]);
    long nmax = pow(10, nmax_exp);
    long ret=fibonacci_full_iteration(n, nmax);
    std::cout << ret << std::endl;
    return EXIT_SUCCESS;
}
