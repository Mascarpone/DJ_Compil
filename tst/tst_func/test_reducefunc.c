/*
 *
 * This test describes the following functionnality of our compiler :
 *
 *      The reduce function applies an associative two-argument function
 *      on the values of a one-dimension table.
 *      Its format is the following :
 *      TYPE reduce(TYPE fct(TYPE a, TYPE b), TYPE array[])
 *
 *
 * The result of our compiler on this code should be :
 *
 *
 *
 *
 * The result of the execution should be :
 *
 *      42
 *
 */


int foo(int a, int b) {
    return a + b;
}


int main() {
    
    int i;
    int T[5] = {2, 3, 5, 11, 21};
    i = reduce(foo, T);
    
    printint(i);
    
    return 0;
}