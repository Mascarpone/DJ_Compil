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
    int[][3] A;
    int i;
    int j;
    for(i = 0; i < 3; i++)
    {
        int[3] B;
        A[i] = B;
        for(j = 0; j < 3; j++) {
            A[i][j] = i+j;
        }
    }

    for(i = 0; i < 3; i++) {
      for(j = 0; j < 3; j++) {
          printint(A[i][j]);
      }
      printchar('\n');
    }
    printchar('\n');
    return 0;
 }
