def sift_down(heap, position, size):
    c = position * 2 + 1
    while c < size:
        if c + 1 < size and heap[c] < heap[c + 1]:
            c += 1
        if heap[c] > heap[position]:
            heap[position], heap[c] = heap[c], heap[position]
            position = c
            c = position * 2 + 1
        else:
            break


def heapify(heap, size):
    last = size / 2 - 1
    for position in reversed(range(last + 1)):
        sift_down(heap, position, size)


def heapsort(series):
    size = len(series)
    heapify(series, size)
    for i in reversed(range(size)):
        series[0], series[i] = series[i], series[0]
        sift_down(series, 0, size - 1)
        size -= 1

if __name__ == '__main__':
    series = [1, 3, 7, 9, -1, 3, 2, 6, 17, 2, 3, 4, 5]
    heapsort(series)
    print series
