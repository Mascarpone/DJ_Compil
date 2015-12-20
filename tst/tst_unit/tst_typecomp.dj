/*
 * Ce test décrit la fonctionnalité suivante du compilateur :
 *      Comparisons between the different types
 *
 * Le résultat attendu de la compilation est :
 *      Pas d'erreur.
 *
 * Le résultat attendu de l'exécution est :
 *
 */

int main() {

    if (2 || 0) {
        print("2 c'est vrai\n");
    }

    if (2 && 0) {
        print("0 c'est faux\n");
    }

    if (1.1 > 1) {
        print("On peut comparer des int et des float\n");
    }

    if ('b' > 'a') {
        print("On peut comparer des char entre eux\n");
    }

    if ('b' > 1) {
        print("On peut comparer des char et des int\n");
    }

    if ('b' > 1.1) {
        print("On peut comparer des char et des float\n");
    }

    return 0;
}
