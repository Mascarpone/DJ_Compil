/*
 * Ce test décrit la fonctionnalité suivante du compilateur :
 *      Passage de tableau par référence
 *
 * Le résultat attendu de la compilation est :
 *      Pas d'erreur.
 *
 * Le résultat attendu de l'exécution est :
 *      affichage de "OK", suivi d'un retour à la ligne
 */

int main()
{
    int[3] A;
    A[0] = 1;
    A[1] = 2;
    A[2] = 3;
    int[] B;
    B = A;
    if(B[0] == 1 && B[1] == 2 && B[2] == 3)
        print("OK\n");
    else
        print("C'est moche...\n");
    return 0;
}
