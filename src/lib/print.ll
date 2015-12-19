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

;@glob.txt = constant [3 x i8] c"abc"
;
;define i32 @main() {
;    %m.s.ptr = alloca %chartable
;    %m.s.size.ptr = getelementptr %chartable* %m.s.ptr, i32 0, i32 0
;    store i32 3, i32* %m.s.size.ptr
;    %txt.first = getelementptr [3 x i8]* @glob.txt, i64 0, i64 0
;    %m.s.buff.ptr = getelementptr %chartable* %m.s.ptr, i32 0, i32 1
;    store i8* %txt.first, i8** %m.s.buff.ptr
;    call void @print(%chartable* %m.s.ptr)
;    ret i32 0
;}
