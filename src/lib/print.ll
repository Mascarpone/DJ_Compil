; Ecrit un tableau de caractères dans la sortie standard

declare void @printchar(i8)

define void @print({ i32, i8* } %ct) {
  %i = alloca i32
  store i32 0, i32* %i
  br label %loopprint_head

loopprint_head:
  %index = load i32* %i
  %size = extractvalue { i32, i8* } %ct, 0
  %again = icmp slt i32 %index, %size
  br i1 %again, label %loopprint_body, label %loopprint_exit

loopprint_body:
  %ct.buff = extractvalue { i32, i8* } %ct, 1
  %ct.elt.ptr = getelementptr i8* %ct.buff, i32 %index
  %ct.elt = load i8* %ct.elt.ptr
  call void @printchar(i8 %ct.elt)
  br label %loopprint_close

loopprint_close:
  %index.next = add i32 %index, 1
  store i32 %index.next, i32* %i
  br label %loopprint_head

loopprint_exit:
  ret void
}
