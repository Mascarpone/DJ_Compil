/*
 * Ce test décrit la fonctionnalité suivante du compilateur :
 *      Lorsqu'on passe en argument un tableau vide à la fonction map
 *      elle retourne un tableau vide du type le type de retour de la
 *      fonction qu'elle prend en paramètre
 *
 * Le résultat attendu de la compilation est :
 *
 *
 * Le résultat attendu de l'exécution est :
 *      Error on line 28 : trying to access to a non permitted memory zone
 */


char foo(int i) {
    
    return 'a';
}


int main() {
    
    int A[];
    char B[];
    B = map(foo, A);
    // ok until this line
    
    printchar(B[0]);
    
    return 0;
}