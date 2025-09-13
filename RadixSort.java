public class RadixSort {
    static int getMax(int arr[]) {
        int max = arr[0];
        for (int i = 1; i < arr.length; i++)
            if (arr[i] > max)
                max = arr[i];
        return max;
    }

    static void countingSort(int arr[], int exp) {
        int n = arr.length;
        int output[] = new int[n];
        int count[] = new int[10];

        for (int i = 0; i < n; i++)
            count[(arr[i] / exp) % 10]++;

        for (int i = 1; i < 10; i++)
            count[i] += count[i - 1];

        for (int i = n - 1; i >= 0; i--) {
            int index = (arr[i] / exp) % 10;
            output[count[index] - 1] = arr[i];
            count[index]--;
        }
        for (int i = 0; i < n; i++)
            arr[i] = output[i];
    }

    static void radixSort(int arr[]) {
        int max = getMax(arr);
        for (int exp = 1; max / exp > 0; exp *= 10)
            countingSort(arr, exp);
    }

    public static void main(String[] args) {
        int arr[] = {170, 45, 75, 90, 802, 24, 2, 66};
        System.out.print("Original: ");
        for (int num : arr) System.out.print(num + " ");
        System.out.println();

        radixSort(arr);

        System.out.print("Sorted: ");
        for (int num : arr) System.out.print(num + " ");
        System.out.println();
    }
}
