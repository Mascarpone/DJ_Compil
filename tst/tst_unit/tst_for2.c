/*
 * Ce test décrit la fonctionnalité suivante du compilateur :
 *      boucle for avec break
 *
 * Le résultat attendu de la compilation est :
 *      Pas d'erreur.
 *
 * Le résultat attendu de l'exécution est :
 *      Affichage des entiers de 0 à 7, un par ligne, suivi d'un retour à la ligne.
 */

int main()
{
    for(int i = 0; i < 12; i++) {
        printint(i);
        print("\n");
        if(i == 7)
            break;
    }
    return 0;
}
