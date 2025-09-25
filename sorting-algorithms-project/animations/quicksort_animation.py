import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def quicksort(arr, frames, low, high):
    if low < high:
        pi = partition(arr, frames, low, high)
        quicksort(arr, frames, low, pi - 1)
        quicksort(arr, frames, pi + 1, high)

def partition(arr, frames, low, high):
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] < pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
            frames.append(list(arr))
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    frames.append(list(arr))
    return i + 1

def animate_quicksort(arr):
    frames = [list(arr)]
    quicksort(arr, frames, 0, len(arr) - 1)
    fig, ax = plt.subplots()
    bar_rects = ax.bar(range(len(arr)), frames[0], align="center", color="skyblue")
    ax.set_title("Quick Sort Animation")
    ax.set_xlim(-0.5, len(arr) - 0.5)
    ax.set_ylim(0, max(arr) * 1.2)

    def update(frame):
        for rect, val in zip(bar_rects, frames[frame]):
            rect.set_height(val)
            rect.set_color("skyblue")
        ax.set_xlabel(f"Step {frame}")
        return bar_rects

    ani = animation.FuncAnimation(
        fig, update, frames=len(frames), interval=200, blit=False, repeat=False
    )
    plt.show()

if __name__ == "__main__":
    arr = [10, 7, 8, 9, 1, 5]
    animate_quicksort(arr)
