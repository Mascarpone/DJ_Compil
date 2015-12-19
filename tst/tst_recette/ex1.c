int square(int x) {
  return x*x;
}

int add(int x,int y) {
  return x+y;
}

int main() {
  int[1000] A;
  int i;
  for (i=0; i<1000; i++) A[i]=i;
  int[1000] B = map(square,A);
  int x=reduce(add,B);
  return 0;
}
