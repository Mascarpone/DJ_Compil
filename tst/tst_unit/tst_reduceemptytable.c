/*
 * Ce test décrit la fonctionnalité suivante du compilateur :
 *      Lorsqu'on passe un tableau vide comme paramètre à la fonction
 *      reduce, cela soulève une erreur à l'éxecution
 *
 * Le résultat attendu de la compilation est :
 *
 *
 * Le résultat attendu de l'exécution est :
 *      Error on line 23 : Tableau vide
 *
 */

int foo(int a, int b)
{
    return 0;
}

int main()
{
    int i;
    int T[];
    i = reduce(foo, T);

    return 0;
}
