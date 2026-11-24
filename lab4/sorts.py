

SHRINK_FACTOR = 1.3
def comb_sort(items, key=None):
    if key is None:
        key = lambda item: item

    gap = len(items)
    swapped = True
    while gap > 1 or swapped:
        gap = max(1, int(gap / SHRINK_FACTOR))
        swapped = False
        for index in range(len(items) - gap):
            other = index + gap
            if key(items[index]) > key(items[other]):
                items[index], items[other] = items[other], items[index]
                swapped = True
    return items


def tournament_sort(items, key=None):
    if key is None:
        key = lambda item: item
    length = len(items)
    if length < 2:
        return items

    keys = [key(item) for item in items]
    size = 1
    while size < length:
        size *= 2

    tree = [-1] * (2 * size)
    for index in range(length):
        tree[size + index] = index

    def winner(left, right):
        if left == -1:
            return right
        if right == -1:
            return left
        return left if keys[left] <= keys[right] else right

    for node in range(size - 1, 0, -1):
        tree[node] = winner(tree[2 * node], tree[2 * node + 1])

    result = []
    for _ in range(length):
        index = tree[1]
        result.append(items[index])
        node = size + index
        tree[node] = -1
        node //= 2
        while node > 0:
            tree[node] = winner(tree[2 * node], tree[2 * node + 1])
            node //= 2

    items[:] = result
    return items
