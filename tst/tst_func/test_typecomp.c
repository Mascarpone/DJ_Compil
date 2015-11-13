/*
 *
 * This test describes the following functionnality of our compiler :
 *
 *      Comparisons between the different types
 *
 *
 * The result of our compiler on this code should be :
 *
 *      Error on line 36 : can't compare char and int
 *      Error on line 40 : can't compare char and float
 *
 * The result of the execution should be :
 *
 *
 **/

int main() {
    
    if (2 || 0) {
        print("2 c'est vrai\n");
    }
    
    if (2 && 0) {
        print("0 c'est faux\n");
    }
    
    if (1.1 > 1) {
        print("On peut comparer des int et des float\n");
    }
    
    if ('b' > 'a') {
        print("On peut comparer des char entre eux\n");
    }
    
    if ('b' > 1) {
        print("On ne peut pas comparer des char et des int\n");
    }
    
    if ('b' > 1.1) {
        print("On ne peut pas comparer des char et des float\n");
    }
    
    return 0;
}