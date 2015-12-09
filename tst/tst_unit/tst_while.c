/*
 * Ce test décrit la fonctionnalité suivante du compilateur :
 *      incrément et while
 *
 * Le résultat attendu de la compilation est :
 *      Pas d'erreur
 *
 * Le résultat attendu de l'exécution est :
 *      Affichage des entiers de 0 à 9, un par ligne.
 *      Pas d'erreur.
 */

extern void printint(int i);

int main()
{
    int i;
    i = 0;
    while(i < 10) {
        printint(i);
        // print("\n");
        i++;
    }
    return 0;
}
