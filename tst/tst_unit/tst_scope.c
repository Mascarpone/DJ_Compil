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


int main()
{
    if(1) {
        int i = 7;
        print("Il est passe par ici\n");
    }
    printint(i);
    return 0;
}
