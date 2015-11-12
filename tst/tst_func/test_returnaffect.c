/*
 *
 * This test describes the following functionnality of our compiler :
 *
 *      The affectation operation returns the affected value
 *      "var = expr" returns "expr"
 *
 *      The integer value 0 means "false" and the others mean "true"
 *
 *
 * The result of our compiler on this code should be :
 *
 *
 *
 * The result of the execution should be :
 *
 *      3... 2... 1... youpi !
 *
 *
 */


int main() {
    
    int x;
    x = 4;
    
    while ((x = x - 1)) {
        printint(x);
        print("... ");
    }
    
    print("youpi !\n");
    
    return 0;
}