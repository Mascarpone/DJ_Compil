/*
 * Ce test décrit la fonctionnalité suivante du compilateur :
 *      Vérifie que l'affectation dans un tableau vérifie bien
 *      que le type des objets qu'ils contient est le même
 *
 * Le résultat attendu de la compilation est :
 *      Error on line 19 : Erreur de typage.
 *
 * Le résultat attendu de l'exécution est :
 *
 */


int main() {

    int A[10];
    char c;

    A[0] = c;

    return 0;
}
