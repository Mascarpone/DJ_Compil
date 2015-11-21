int main() {
  int A[1000];
  int i,x;
  x=0;
  for (i=0; i<1000; i++) {
    A[i]=i;
  }
  for (i=0; i<1000; i++) {
    x+=A[i]*A[i];
  }
  return x;
}
