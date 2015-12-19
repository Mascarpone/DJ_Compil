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

//extern void print(char[] A);
extern void printint(int i);

int main()
{
    int[3] A;

    A[0] = 1;
    A[1] = 2;
    A[2] = 3;
    if((A[0] == 1) && (A[1] == 2) && (A[2] == 3))
        //print("OK\n");
        printint(1);
    else
        //print("C'est moche...\n");
        printint(0);
    return 0;
}
