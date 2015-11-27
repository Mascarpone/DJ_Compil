#include <stdio.h>
#include <stdlib.h>

// Version non vectorisée
#define TYPE reduce(TYPE fct(TYPE a, TYPE b), TYPE array[SIZE]) ({    \
          if (SIZE < 2) exit(EXIT_FAILURE);                           \
          int i;                                                      \
          TYPE ret = fct(array[0], array[1]);                         \
          for (i = 2; i < SIZE; i++) {                                \
            ret = fct(ret, array[i]);                                 \
          }                                                           \
          return ret;                                                 \
        })
