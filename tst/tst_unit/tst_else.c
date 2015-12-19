/*
 * Ce test décrit la fonctionnalité suivante du compilateur :
 *      décrément
 *      if avec clause else if et else
 *
 * Le résultat attendu de la compilation est :
 *      Pas d'erreur.
 *
 * Le résultat attendu de l'exécution est :
 *      Affichage de "+.-".
 *      Pas d'erreur.
 */

 extern void printchar(char a);

int main()
{
    int a = 1;
    if(a > 0)
        printchar('+');
    else if(a == 0)
        printchar('.');
    else
        printchar('-');

    a--;
    if(a > 0)
        printchar('+');
    else if(a == 0)
        printchar('.');
    else
        printchar('-');

    a--;
    if(a > 0)
        printchar('+');
    else if(a == 0)
        printchar('.');
    else
        printchar('-');

    return 0;
}
