/*
 *
 * This test describes the following functionnality of our compiler :
 *
 *      The "else" keyword corresponds to the last "if" or "else if" clause.
 *
 *
 * The result of our compiler on this code should be :
 *
 *
 *
 * The result of the execution should be :
 *
 *      good job compiler !
 *
 *
 */


int main() {
    
    int i;
    i = 0;
    
    if (1 == 0) {
        if (i > 0) {
            print("something");
        }
        else {
            print("something else");
        }
    }
    else if (-1 == 0) {
        print("lol -1 == 0");
    }
    else {
        print("good job compiler !");
    }
    
    return 0;
}