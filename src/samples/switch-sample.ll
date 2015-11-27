; Exemple de switch traduite en llvm
;
;switch-sample.dj
;=============
;void printint(int);
;void printchar(char);
;
;int main() {
;   int i;
;   i = 12;
;   switch (i) {
;   case 0:
;       printint(0);
;       break;
;   case 12:
;       printint(12);
;       break;
;   default:
;       printchar('X');
;       break;
;   }
;   return 0;
;}
;
;switch-sample.ll
;=============
declare void @printint(i32)
declare void @printchar(i8)

define i32 @main() {
    %i = alloca i32
    store i32 12, i32* %i
    br label %switch_head

switch_head:
    %i.val = load i32* %i
    switch i32 %i.val, label %switch_default [i32 0, label %switch_on0
                                              i32 12, label %switch_on12]

switch_on0:
    call void @printint(i32 0)
    br label %switch_exit

switch_on12:
    call void @printint(i32 12)
    br label %switch_exit

switch_default:
    call void @printchar(i8 88)
    br label %switch_exit

switch_exit:
    ret i32 0
}
