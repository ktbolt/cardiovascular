#file test_fib.py
import fibonacci
import time
 
class Timer:
    def __enter__(self):
        self.start = time.clock()
        return self
 
    def __exit__(self, *args):
        self.end = time.clock()
        self.interval = self.end - self.start
 
def fibonacci_recursion_py(n):
    a = 1
    if(n >= 2):
        a = fibonacci_recursion_py(n-1) + fibonacci_recursion_py(n-2);
    return a;
 
def fibonacci_iteration_py(n, nmax):
    a = 0;
    b = 1;
    temp = 0;
    for i in range(n):
    # while(a<=n):
    # for( long i = 0; i + a <=n ; b = i ) {
        temp = (a + b) % nmax;
        a = b;
        b = temp;
    return a
 
if __name__ == '__main__':
    with Timer() as t1:
        fibonacci_recursion_py(30)
    print t1.interval
    with Timer() as t2:
        fibonacci.fibonacci_recursion(30)
    print t2.interval
 
    num_of_iterations = int(20000)
    N_MAX = int(1e14)
    with Timer() as t3:
        n0 = 0
        for i in range(num_of_iterations):
            n0+=fibonacci_iteration_py(i,N_MAX)
    print str(n0) + ", " + str(t3.interval)
 
    with Timer() as t4:
        n0=0
        for i in range(num_of_iterations):
            n0+=fibonacci.fibonacci_iteration(i, N_MAX)
    print str(n0) + ", " + str(t4.interval)
 
    with Timer() as t5:
        n0=fibonacci.fibonacci_full_iteration(num_of_iterations, N_MAX)
    print str(n0) + ", " + str(t5.interval)