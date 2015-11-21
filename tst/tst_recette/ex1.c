int square(int x) {
  return x*x;
}

int add(int x,int y) {
  return x+y;
}

int main() {
  int A[1000];
  int i, x;
  for (i=0; i<1000; i++) A[i]=i;
  x=reduce(add,map(square,A));
  return x;
}
