/*
 * Ce test décrit la fonctionnalité suivante du compilateur :
 *      tableaux à plusieurs dimensions
 *
 * Le résultat attendu de la compilation est :
 *      Pas d'erreur.
 *
 * Le résultat attendu de l'exécution est :
 *      Affiche :
 *      012
 *      123
 *      234
 */

int main()
{
    int[] A[3];
    for(int i = 0; i < 3; i++)
    {
        int B[3];
        A[i] = B;
        for(int j = 0; j < 3; j++) {
            A[i][j] = i+j;
        }
    }

    for(int i = 0; i < 3; i++) {
        for(int j = 0; j < 3; j++) {
            printint(A[i][j]);
        }
        printchar('\n');
    }
    printchar('\n');
    return 0;
 }
