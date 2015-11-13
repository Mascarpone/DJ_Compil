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

char foo (int i)
{
    char a;
    int span;

    span = 'z' - 'a' + 1;
    a = (char) ((i % span) + 'a');

    return a;
}

int main()
{
    int T[5];
    T[0] = 24;
    T[1] = 40;
    T[2] = 72;
    T[3] = 15;
    T[4] = 8;
    char W[5] = map(foo, T);

    int i;
    for (i = 0; i < 5; i = i + 1) {
        printchar(W[i]);
    }

    free(W);

    return 0;
}
