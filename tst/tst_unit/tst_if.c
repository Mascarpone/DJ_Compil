/*
 * Ce test décrit la fonctionnalité suivante du compilateur :
 *      Tests logiques et if
 *
 * Le résultat attendu de la compilation est :
 *      Pas d'erreur.
 *
 * Le résultat attendu de l'exécution est :
 *      Affichage de "Pyvain" suivi d'un retour à la ligne.
 *      Pas d'erreur.
 */

int main()
{
    int a = 12;
    if(a)
        print("P");
    if(a == 21)
        print("flevern");
    if(a < 144) {
        print("y");
        print("va");
    }
    if(a != 641)
        print("in");
    if(!0)
        print("\n");
    return 0;
}
