/*
 * Ce test décrit la fonctionnalité suivante du compilateur :
 *      création et appel de fonction
 *
 * Le résultat attendu de la compilation est :
 *      Pas d'erreur
 *
 * Le résultat attendu de l'exécution est :
 *      Affichage de "12" suivi d'un retour à la ligne.
 */

int bar(int a, int b)
{
    return a+b;
}

int main()
{
    int x = 2;
    printint(bar(x,10));
    print("\n");
    return 0;
}
