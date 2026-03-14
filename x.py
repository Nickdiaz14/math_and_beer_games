import random

def radix_sort(list):
    final_list = list.copy()
    b_list = []
    digits = 0
    for item in list:
        value = f"{item:b}"
        b_list.append(value)
        if len(value) > digits:
            digits = len(value)
    b_list = [num.zfill(digits) for num in b_list]
    for i in range(1, digits + 1):
        for j in range(len(b_list)):
            actual_number = b_list[j]
            if actual_number[-i] == "1":
                b_list[j] = 'x'
                b_list.append(actual_number)
        b_list = [num for num in b_list if num != 'x']
    
    return [int(n, 2) for n in b_list]

lista = [random.randint(0, 20000) for _ in range(20)]
print(lista)
print(radix_sort(lista))

def radix_sort_optimized(arr):
    if not arr:
        return arr

    max_bits = max(arr).bit_length()
    res = arr.copy()

    for i in range(max_bits):
        zeros = []
        ones = []

        for num in res:
            if (num >> i) & 1:
                ones.append(num)
            else:
                zeros.append(num)

        res = zeros + ones

    return res

print(radix_sort_optimized(lista))
