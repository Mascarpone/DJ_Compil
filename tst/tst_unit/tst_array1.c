/*
 * Ce test décrit la fonctionnalité suivante du compilateur :
 *      if else
 *      Et logique (&&)
 *      Création de tableau
 *      Affectation et lecture de contenu de tableau
 *
 * Le résultat attendu de la compilation est :
 *      Pas d'erreur.
 *
 * Le résultat attendu de l'exécution est :
 *      affichage de "OK", suivi d'un retour à la ligne
 */

int main()
{
    int A[3];
    A[0] = 1;
    A[1] = 2;
    A[2] = 3;
    if(A[0] == 1 && A[1] == 2 && A[2] == 3)
        print("OK\n");
    else
        print("C'est moche...\n");
    return 0;
}
