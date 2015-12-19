/*
 * Ce test décrit la fonctionnalité suivante du compilateur :
 *      création et appel de fonction
 *
 * Le résultat attendu de la compilation est :
 *      Pas d'erreur
 *
 * Le résultat attendu de l'exécution est :
 *      Affichage de "3" suivi d'un retour à la ligne.
 */


int foo()
{
    return 3;
}

int main()
{
    printint(foo());
    print("\n");
    return 0;
}
