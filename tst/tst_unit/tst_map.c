/*
 * Ce test décrit la fonctionnalité suivante du compilateur :
 *      référence de fonction
 *      map()
 *      for
 *      if
 *
 * Le résultat attendu de la compilation est :
 *      Pas d'erreur.
 *
 * Le résultat attendu de l'exécution est :
 *      Affichage de "ok" suivi d'un retour à la ligne.
 */

int square(int a)
{
    return a*a;
}

int main()
{
    int A[16]
    for(int i = 0; i < 16; i++)
        A[i] = i;
    int B[] = map(foo, A);
    int ok = 1;
    for(int i = 0; i < 16; i++)
        if(B[i] != i*i)
            ok = 0;
    if(ok)
        print("ok\n");
    else
        print("echec\n");
}
