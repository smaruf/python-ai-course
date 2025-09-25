import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Radix sort with frames capturing
def radix_sort_with_frames(arr):
    frames = []
    arr = list(arr)
    max_num = max(arr)
    exp = 1
    frames.append(list(arr))
    while max_num // exp > 0:
        arr = counting_sort_with_frames(arr, exp, frames)
        exp *= 10
    return frames

def counting_sort_with_frames(arr, exp, frames):
    n = len(arr)
    output = [0] * n
    count = [0] * 10

    # Count occurrences
    for i in range(n):
        index = arr[i] // exp
        count[index % 10] += 1

    for i in range(1, 10):
        count[i] += count[i - 1]

    for i in range(n - 1, -1, -1):
        index = arr[i] // exp
        output[count[index % 10] - 1] = arr[i]
        count[index % 10] -= 1

    # Save frame after each counting sort pass
    frames.append(list(output))
    return output

# Animation code
def animate_radix_sort(arr):
    frames = radix_sort_with_frames(arr)

    fig, ax = plt.subplots()
    bar_rects = ax.bar(range(len(arr)), frames[0], align="center")
    ax.set_title("Radix Sort Animation")
    ax.set_xlim(-0.5, len(arr) - 0.5)
    ax.set_ylim(0, max(arr) * 1.2)

    def update(frame):
        for rect, val in zip(bar_rects, frames[frame]):
            rect.set_height(val)
            rect.set_color("skyblue")
        ax.set_xlabel(f"Pass {frame}")
        return bar_rects

    ani = animation.FuncAnimation(
        fig, update, frames=len(frames), interval=120, blit=False, repeat=False
    )
    plt.show()

if __name__ == "__main__":
    arr = [170, 45, 75, 90, 802, 24, 2, 66]
    animate_radix_sort(arr)
