; Ecrit un tableau de caractères dans la sortie standard

declare void @printchar(i8)

%chartable = type {
  i32, ; size
  i8*  ; content
}

define void @print(%chartable* %ct) {
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
  %ct.content.ptr = getelementptr %chartable* %ct, i32 0, i32 1
  %ct.content = load i8** %ct.content.ptr
  %ct.i = getelementptr i8* %ct.content, i32 %i.val
  %ct.i.val = load i8* %ct.i
  call void @printchar(i8 %ct.i.val)
  br label %loopprint_close

loopprint_close:
  %i.1 = load i32* %i
  %i.2 = add i32 %i.1, 1
  store i32 %i.2, i32* %i
  br label %loopprint_head

loopprint_exit:
  ret void
}

@glob.txt = constant [3 x i8] c"abc"

define i32 @main() {
    %m.s.ptr = alloca %chartable
    %m.size.ptr = getelementptr %chartable* %m.s.ptr, i32 0, i32 0
    %m.buff.ptr = getelementptr %chartable* %m.s.ptr, i32 0, i32 1
    %txt.first = getelementptr [3 x i8]* @glob.txt, i64 0, i64 0
    store i32 3, i32* %m.size.ptr
    store i8* %txt.first, i8** %m.buff.ptr
    call void @print(%chartable* %m.s.ptr)
    ret i32 0
}
