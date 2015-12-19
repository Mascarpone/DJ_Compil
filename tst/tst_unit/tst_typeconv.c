/*
 * Ce test décrit la fonctionnalité suivante du compilateur :
 *      Vérifie les casts
 *
 * Le résultat attendu de la compilation est :
 *      Pas d'erreur.
 *
 * Le résultat attendu de l'exécution est :
 *      Pas d'erreur.
 */

int main() {

    int a = 1;
    float b = 1.3;

    b = a; // OK

    return 0;
}
