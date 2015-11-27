; Exemple de clause if
;
;if-sample.dj
;=============
;void printchar(char);
;
;int main() {
;   int i;
;   i = 0;
;   if (i > 0) {
;     printchar('o');
;   } else {
;     printchar('n');
;   }
;   return 0;
;}
;
;if-sample.ll
;=============
declare void @printchar(i8)

define i32 @main() {
    %i = alloca i32
    store i32 0, i32* %i
    br label %if_head

if_head:
    %i.val = load i32* %i
    %bool = icmp sgt i32 %i.val, 0
    br i1 %bool, label %if_body, label %if_else

if_body:
    call void @printchar(i8 111)
    br label %if_end

if_else:
    call void @printchar(i8 110)
    br label %if_end

if_end:
    ret i32 0
}
