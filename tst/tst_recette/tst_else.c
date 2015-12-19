/*
 * Ce test décrit la fonctionnalité suivante du compilateur :
 *      if et else
 *
 * Le résultat attendu de la compilation est :
 *      Pas d'erreur.
 *
 * Le résultat attendu de l'exécution est :
 *      Affichage de "Bravo compilateur !", suivi d'un retour à la ligne.
 */

extern void print(char[] c);

int main()
{
    int i = 0;

    if (1 == 0) {
        if (i > 0) {
            print("Quelque chose\n");
        } else {
            print("Quelque chose d'autre\n");
        }
    } else if (-1 == 0) {
        print("lol -1 == 0\n");
    } else {
        print("Bravo compilateur !\n");
    }

    return 0;
}
