/*
 * Ce test décrit la fonctionnalité suivante du compilateur :
 *      décrément
 *      if avec clause else if et else
 *
 * Le résultat attendu de la compilation est :
 *      Pas d'erreur.
 *
 * Le résultat attendu de l'exécution est :
 *      Affichage de "+.-" suivi d'un retour à la ligne.
 *      Pas d'erreur.
 */

int main()
{
    int a = 1;
    if(a > 0)
        print("+");
    else if(a == 0)
        print(".");
    else
        print("-");

    a--;
    if(a > 0)
        print("+");
    else if(a == 0)
        print(".");
    else
        print("-");

    a--;
    if(a > 0)
        print("+");
    else if(a == 0)
        print(".");
    else
        print("-");

    print("\n");
    return 0;
}
