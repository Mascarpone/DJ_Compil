; Ecrit un tableau de caractères dans la sortie standard

declare void @printchar(i8)

%chartable = type {
  i32, ; size
  i8*  ; content
}

define void @print(%chartable* %ct) { ; changer le parametre en fonction de comment sont déninis nos tableaux
  %i = alloca i32
  store i32 0, i32* %i
  br label %loopprint_head

loopprint_head:
  %index = load i32* %i
  %afterptr = getelementptr %chartable* %ct, i32 0, i32 0
  %after = load i32* %afterptr
  %again = icmp slt i32 %index, %after
  br i1 %again, label %loopprint_body, label %loopprint_exit

loopprint_body:
  %size = getelementptr %chartable* %ct, i32 0, i32 0
  %i.val = load i32* %i
  %ct.content = getelementptr %chartable* %ct, i32 0, i32 1
  %ct.i = getelementptr(i8* %ct.content, i32 0, i32 %i.val)  ;;;;;; TODO : Modifier pour accéder à la bonne case du tableau
  %ct.i.val = load i8* %ct.i
  call void @printchar(i8 %ct.i.val)
  br label %loopprint_close

loopprint_close:
  %i.1 = load i32* %i
  %i.2 = add i32 %i.1, 1
  store i32 %i.2, i32* %i
  br label %loopprint_head

loopprint_exit:
}
