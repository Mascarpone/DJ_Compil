/*
 * Ce test décrit la fonctionnalité suivante du compilateur :
 *      boucle for
 *
 * Le résultat attendu de la compilation est :
 *      Pas d'erreur.
 *
 * Le résultat attendu de l'exécution est :
 *      Affichage des entiers de 0 à 11, un par ligne, suivi d'un retour à la ligne.
 */

int main()
{
    int i;
    for(i = 0; i < 12; i++) {
        printint(i);
        print("\n");
    }
    return 0;
}
