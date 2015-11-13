/*
 *
 * This test describes the following functionnality of our compiler :
 *
 *      Check that table affectation verifies the type of the objects they contain
 *
 *
 * The result of our compiler on this code should be :
 *
 *      Error on line 24 : can't convert char to int
 *
 *
 * The result of the execution should be :
 *
 *
 **/


int main() {
    
    int A[10];
    char c;
    
    A[0] = c;
    
    return 0;
}