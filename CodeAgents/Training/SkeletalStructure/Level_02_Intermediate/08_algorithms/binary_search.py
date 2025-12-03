def binary_search(arr, target):
    low = 0
    high = len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1

if __name__ == "__main__":
    my_list = [2, 3, 4, 10, 40]
    target = 10
    result = binary_search(my_list, target)
    if result != -1:
        print(f"Element is present at index {result}")
    else:
        print("Element is not present in array")
