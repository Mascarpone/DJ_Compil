/*
 *
 * This test describes the following functionnality of our compiler :
 *
 *      Some words are keywords and so are reserved.
 *      Variables and functions can't take these for their names.
 *
 * The result of our compiler on this code should be :
 *
 *      Error on line 20 : unexpected format for variable declaration
 *      Error on line 24 : function map is defined more than once
 *      Error on line 31 : keyword for is reserved
 *      Error on line 32 : keyword if is reserved
 *      Error on line 33 : keyword else is reserved
 *      Error on line 34 : unexpected format for variable declaration
 *
 **/


int int(int i) { // Error
    return i;
}
 
void map() { // Error
    
}

int main() {
    
    int main; // OK (thanks to the scope)
    int for; // Error
    int if; // Error
    int else; // Error
    int int; // Error
    
    return 0;
}