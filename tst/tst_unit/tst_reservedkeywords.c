/*
 * Ce test décrit la fonctionnalité suivante du compilateur :
 *      Certains mots sont des mots-clés et sont donc réservés
 *      Les variables et les fonctions ne peuvent pas les prendre comme nom
 *
 * Le résultat attendu de la compilation est :
 *      Error on line 18 : mot clé int reservé
 *      Error on line 23 : mot clé map réservé
 *      Error on line 30 : mot clé for réservé
 *      Error on line 31 : mot clé if réservé
 *      Error on line 32 : mot clé else réservé
 *      Error on line 33 : mot clé int réservé
 *
 * Le résultat attendu de l'exécution est :
 *
 */

int int(int i)
{ // Error
    return i;
}

void map()
{ // Error
    print("map");
}

int main()
{
    int main; // OK (thanks to the scope)
    int for; // Error
    int if; // Error
    int else; // Error
    int int; // Error

    return 0;
}
