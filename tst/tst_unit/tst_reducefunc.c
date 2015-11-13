/*
 * Ce test décrit la fonctionnalité suivante du compilateur :
 *      La fonction reduce applique une fonction d’arité 2 associative
 *      sur l’ensemble des éléments d’un tableau à une dimension pour le réduire
 *      Elle a pour prototype : TYPE reduce(TYPE fct(TYPE a, TYPE b), TYPE array[])
 *
 * Le résultat attendu de la compilation est :
 *
 *
 * Le résultat attendu de l'exécution est :
 *      42
 *
 */


int foo(int a, int b)
{
    return a + b;
}


int main()
{
    int i;
    int T[5] = {2, 3, 5, 11, 21};
    i = reduce(foo, T);

    printint(i);

    return 0;
}
