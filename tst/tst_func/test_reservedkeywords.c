/*
 * Ce test décrit la fonctionnalité suivante du compilateur :
 *      Certains mots sont des mots-clés et sont donc réservés
 *      Les variables et les fonctions ne peuvent pas les prendre comme nom
 *
 * Le résultat attendu de la compilation est :
 *      Error on line 20 : unexpected format for variable declaration
 *      Error on line 24 : function map is defined more than once
 *      Error on line 31 : keyword for is reserved
 *      Error on line 32 : keyword if is reserved
 *      Error on line 33 : keyword else is reserved
 *      Error on line 34 : unexpected format for variable declaration
 *
 * Le résultat attendu de l'exécution est :
 *
 */



int int(int i) { // Error
    return i;
}
 
void map() { // Error
    
}

int main() {
    
    int main; // OK (thanks to the scope)
    int for; // Error
    int if; // Error
    int else; // Error
    int int; // Error
    
    return 0;
}