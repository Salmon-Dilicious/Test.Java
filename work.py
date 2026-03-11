import random
import time

# Insertion Sort
# Time Complexity: O(n²) - worst case and average case
def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j+1] = arr[j]
            j -= 1
        arr[j+1] = key
    return arr


# Bubble Sort
# Time Complexity: O(n²) - worst case and average case
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr


# Merge Sort
# Time Complexity: O(n log n) - best, average, and worst case
def merge_sort(arr):
    if len(arr) > 1:
        mid = len(arr)//2
        left = arr[:mid]
        right = arr[mid:]

        merge_sort(left)
        merge_sort(right)

        i=j=k=0

        while i < len(left) and j < len(right):
            if left[i] < right[j]:
                arr[k]=left[i]
                i+=1
            else:
                arr[k]=right[j]
                j+=1
            k+=1

        while i < len(left):
            arr[k]=left[i]
            i+=1
            k+=1

        while j < len(right):
            arr[k]=right[j]
            j+=1
            k+=1

    return arr


# Quick Sort
# Time Complexity: O(n log n) - average case, O(n²) - worst case
def quick_sort(arr):
    if len(arr) <= 1:
        return arr

    pivot = arr[len(arr)//2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]

    return quick_sort(left) + middle + quick_sort(right)


# Main Program
if __name__ == "__main__":
    # Generate random array
    test_array = [random.randint(1, 1000) for _ in range(1000)]
    
    print("Original array:")
    print(test_array)
    print()
    
    # Test Insertion Sort
    arr1 = test_array.copy()
    start = time.time()
    result1 = insertion_sort(arr1)
    end = time.time()
    print(f"Insertion Sort Result: {result1}")
    print(f"Time: {end - start:.6f} seconds")
    print()
    
    # Test Bubble Sort
    arr2 = test_array.copy()
    start = time.time()
    result2 = bubble_sort(arr2)
    end = time.time()
    print(f"Bubble Sort Result: {result2}")
    print(f"Time: {end - start:.6f} seconds")
    print()
    
    # Test Merge Sort
    arr3 = test_array.copy()
    start = time.time()
    result3 = merge_sort(arr3)
    end = time.time()
    print(f"Merge Sort Result: {result3}")
    print(f"Time: {end - start:.6f} seconds")
    print()
    
    # Test Quick Sort
    arr4 = test_array.copy()
    start = time.time()
    result4 = quick_sort(arr4)
    end = time.time()
    print(f"Quick Sort Result: {result4}")
    print(f"Time: {end - start:.6f} seconds")