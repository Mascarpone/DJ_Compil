/*
 * Ce test décrit la fonctionnalité suivante du compilateur :
 *      Fonction map()
 *
 * Le résultat attendu de la compilation est :
 *      Pas d'erreur.
 *
 * Le résultat attendu de l'exécution est :
 *      youpi
 */

char foo (char i)
{
    char a;
    char span;

    span = 'z' - 'a' + 1;
    a = (i % span) + 'a';

    return a;
}

int main()
{
    int[5] T;
    T[0] = 24;
    T[1] = 40;
    T[2] = 72;
    T[3] = 15;
    T[4] = 8;
    char[5] W = map(foo, T);

    int i;
    for (i = 0; i < 5; i = i + 1) {
        printchar(W[i]);
    }

    free(W);

    return 0;
}
