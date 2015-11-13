/*
 *
 * This test describes the following functionnality of our compiler :
 *
 *      In this language, tables can be affected by other tables
 *      since the affected table has the same type and is smaller
 *      than the table it is affected by
 *
 * The result of our compiler on this code should be :
 *
 *      Error on line 26 : cannot assign a table in a larger one
 *
 *
 **/


int main() {
    
    int A[100];
    int B[];
    int C[200];
    int D[50];
    int E[];
    int F[];
    B = A; // OK B has 100 elements
    C = A; // Error
    D = A; // OK D has 100 elements
    D = B; // OK D has 100 elements
    E = F; // OK
    
    return 0;
}