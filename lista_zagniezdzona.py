def flatten_list(nested_list: list) -> list:
    flat_list = []
    for item in nested_list:
        if isinstance(item, list):
            flat_list.extend(flatten_list(item))
        else:
            flat_list.append(item)
    return flat_list

if __name__ == '__main__':
    print(flatten_list([1, 2, 3]))
    print(flatten_list([1, [2, 3], [4, [5]]]))
    print(flatten_list([]))
    print(flatten_list([[[1]]]))
    print(flatten_list([1, [2, [3, [4]]]]))
