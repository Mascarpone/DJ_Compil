#include <stdio.h>
#include <stdlib.h>

// Version non vectorisée
#define TYPE2[SIZE] map(TYPE2 fct(TYPE1), TYPE1 array[SIZE]) ({   \  // changer la valeur de retour en fonction de notre implémentation des tableaux
          int i;                                                  \
          TYPE2[SIZE] ret;                                        \
          for (i = 0; i < SIZE; i++) {                            \
            ret[i] = fct(array[i]);                               \
          }                                                       \
          return ret;                                             \
        })
