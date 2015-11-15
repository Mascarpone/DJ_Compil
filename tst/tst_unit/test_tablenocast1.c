/*
 * Ce test décrit la fonctionnalité suivante du compilateur :
 *      Vérifie que l'affectation entre les tableaux vérifie bien
 *      que le type des objets qu'ils contiennent est le même
 *
 * Le résultat attendu de la compilation est :
 *      Error on line 19 : table with different object types can't be affected to each other
 *
 * Le résultat attendu de l'exécution est :
 *
 */


int main() {
    
    int A[10];
    char B[];
    
    B = A;
    
    return 0;
}