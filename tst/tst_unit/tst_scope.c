/*
 * Ce test décrit la fonctionnalité suivante du compilateur :
 *      Les variables ne sont valides que dans le bloc où elles ont été déclarées
 *
 * Le résultat attendu de la compilation est :
 *      Erreur ligne 18 : la variable i n'est pas définie.
 *
 * Le résultat attendu de l'exécution est :
 *      Pas d'exécutable.
 */

extern void printint(int i);

int main()
{
    if(1) {
        int i = 7;
        //print("Il est passé par ici\n");
    }
    printint(i);
    return 0;
}
