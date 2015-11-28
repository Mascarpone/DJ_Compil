;
;#include <stdio.h>
;#include <stdlib.h>
;
;struct chartable {
;  int size;
;  char* content;
;};
;
;void print(struct chartable* A) {
;  int i;
;  for (i = 0; i < A->size; i++)
;    printf("%c", A->content[i]);
;}
;
;int main() {
;  struct chartable A;
;  A.size = 1;
;  A.content = malloc(A.size * sizeof(char));
;  A.content[0] = 'X';
;  print(&A);
;  free(A.content);
;  return 0;
;}
;

; redéfini le structure (sinon ne connait pas la taille à la compilation) ;; Y A T IL UNE FACON DE DECLARE OU INCLUDE ??
%chartable = type {
  i32, ; size
  i8*  ; content
}

declare i8* @malloc(i64)
declare void @free(i8*)
declare void @print(%chartable*)

define i32 @main() {
  ; alloue la structure
  %A = alloca %chartable

  ; set le champ size
  %A.size = getelementptr inbounds %chartable* %A, i32 0, i32 0
  store i32 1, i32* %A.size

  ; récupère le champ size et le convertit en i64 (pour malloc)
  %A.size.reload = getelementptr inbounds %chartable* %A, i32 0, i32 0
  %A.size.val = load i32* %A.size.reload
  %A.size.val64 = sext i32 %A.size.val to i64

  ; alloue le champ content du chartable
  %A.content.size = mul i64 %A.size.val64, 1
  %allocate = call i8* @malloc(i64 %A.content.size)
  %A.content = getelementptr inbounds %chartable* %A, i32 0, i32 1
  store i8* %allocate, i8** %A.content

  ; set content[0]
  %A.content.reload = getelementptr inbounds %chartable* %A, i32 0, i32 1
  %A.content.0.adr = load i8** %A.content.reload
  %A.content.0.val = getelementptr inbounds i8* %A.content.0.adr, i64 0
  store i8 88, i8* %A.content.0.val
  call void @print(%chartable* %A)

  ; libère la mémoire allouée
  %A.content.reloadforfree = getelementptr inbounds %chartable* %A, i32 0, i32 1
  %A.content.adr = load i8** %A.content.reloadforfree
  call void @free(i8* %A.content.adr)

  ret i32 0
}
