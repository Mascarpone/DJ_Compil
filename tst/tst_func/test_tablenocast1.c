/*
 *
 * This test describes the following functionnality of our compiler :
 *
 *      Check that table affectation verifies the type of the objects they contain
 *
 *
 * The result of our compiler on this code should be :
 *
 *      Error on line ?? : table with different object types can't be affected to each other
 *
 *
 * The result of the execution should be :
 *
 *
 **/


int main() {
    
    int A[10];
    char B[];
    
    B = A;
    
    return 0;
}