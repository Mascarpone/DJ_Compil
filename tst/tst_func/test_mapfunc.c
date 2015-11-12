/*
 *
 * This test describes the following functionnality of our compiler :
 *
 *      The map function applies a one-argument function on each value of a one-dimension table
 *      Its format is the following :
 *      TYPE2 (map(TYPE2 fct(TYPE1),TYPE1 array[N]))[N]
 *
 *
 * The result of our compiler on this code should be :
 *
 *
 *
 * The result of the execution should be :
 *
 *      youpi
 *
 *
 **/

char foo (int i) {
    char a;
    int span;
    
    span = 'z' - 'a' + 1;
    a = (char) ((i % span) + 'a');
    
    return a;
}

int main() {
    
    int T[5] = {24, 40, 72, 15, 8};
    char W[5] = map(foo, T);
    
    int i;
    for (i = 0; i < 5; i = i + 1) {
        printchar(W[i]);
    }
    
    free(W);
    
    return 0;
}

