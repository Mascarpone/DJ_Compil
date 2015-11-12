/*
 *
 * This test describes the following functionnality of our compiler :
 *
 *      When passing an empty table to the map function, 
 *      returns an empty table of type the returned type of the function in parameter
 *
 *
 * The result of our compiler on this code should be :
 *
 *      Error on line 29 : trying to access to a non permitted memory zone
 *
 *
 **/


char foo(int i) {
    
    return 'a';
}


int main() {
    
    int A[];
    char B[];
    B = map(foo, A);
    // ok until this line
    
    printchar(B[0]);
    
    return 0;
}