#include <iostream>
#include <stdlib.h>

#define random(x) (rand()%x)
#define N (100)

using namespace std;

int print_array(int *a, int num)
{
    for (int i=0; i<num; ++i) {
        cout << a[i] << ' ';
        if (i % 10 == 9)
            cout << endl;
    }
    cout << endl;
    return 0;
}

int swap(int *a, int *b)
{
    int temp = *a;
    *a = *b;
    *b = temp;
    return 0;
}

int quick_sort(int *a, int start, int end)
{
    /*
     * 快排递归
     */

    if (a == NULL)
        return -1;

    if (start >= end)
        return 0;

    int i = start;
    int j = end;


    while (i < j) {
        /*
         * 要从右边先找，才能找到正确的位置
         */
        while (i < j && a[j] >= a[start] && --j);
        while (i < j && a[i] <= a[start] && ++i);
        swap(a + i, a + j);
    }
    swap(a + start, a + i);

    quick_sort(a, start, i - 1);
    quick_sort(a, i + 1, end);

    return 0;
}

int main(int argc, const char *argv[])
{
    int a[N];
    srand(time(0));

    for (int i=0; i<N; ++i) {
        a[i] = random(N);
    }

    print_array(a, N);
    quick_sort(a, 0, N-1);
    print_array(a, N);

    return 0;
}
