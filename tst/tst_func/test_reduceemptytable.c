/*
 *
 * This test describes the following functionnality of our compiler :
 *
 *      When passing an empty table to the reduce function, the compiler raises an error
 *
 *
 * The result of our compiler on this code should be :
 *
 *      Error on line 26 : reduce function needs a non-empty table as its parameter
 *
 *
 */


int foo(int a, int b) {
    
    return 0;
}


int main() {
    
    int i;
    int T[];
    i = reduce(foo, T);
    
    return 0;
}