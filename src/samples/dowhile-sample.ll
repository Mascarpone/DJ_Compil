; Exemple de boucle do-while traduite en llvm
;
;dowhile-sample.dj
;=============
;void printint(int);
;
;int main() {
;   int i;
;   i = 0;
;   do {
;     i++;
;     printint(i);
;   } while (i < 9);
;   return 0;
;}
;
;dowhile-sample.ll
;=============
declare void @printint(i32)

define i32 @main() {
    %i = alloca i32
    br label %loop_init

loop_init:
    store i32 0, i32* %i
    br label %loop_body

loop_body:
    %i.0 = load i32* %i
    %i.1 = add i32 %i.0, 1
    store i32 %i.1, i32* %i
    call void @printint(i32 %i.1)
    br label %loop_tail

loop_tail:
    %index = load i32* %i
    %again = icmp slt i32 %index, 9
    br i1 %again, label %loop_body, label %loop_exit

loop_exit:
    ret i32 0
}
