; Exemple de boucle while traduite en llvm
;
;while-sample.dj
;=============
;void printint(int);
;
;int main() {
;   int i;
;   while(i < 10) {
;       printint(i);
;       i++;
;   }
;   return 0;
;}
;
;while-sample.ll
;=============
declare void @printint(i32)

define i32 @main() {
    %i = alloca i32
    br label %loop_init

loop_init:
    store i32 0, i32* %i
    br label %loop_head

loop_head:
    %index = load i32* %i
    %again = icmp slt i32 %index, 10
    br i1 %again, label %loop_body, label %loop_exit

loop_body:
    %i.0 = load i32* %i
    call void @printint(i32 %i.0)
    %i.1 = add i32 %i.0, 1
    store i32 %i.1, i32* %i
    br label %loop_head

loop_exit:
    ret i32 0
}
