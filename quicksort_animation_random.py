import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Generate 10,000 random numbers
arr = np.random.randint(0, 100000, size=10000)
frames = []

def quicksort(arr, low, high, step=50):
    if low < high:
        pi = partition(arr, low, high)
        if len(frames) == 0 or len(frames) % step == 0:
            frames.append(np.copy(arr))
        quicksort(arr, low, pi - 1, step)
        quicksort(arr, pi + 1, high, step)

def partition(arr, low, high):
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] < pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1

# Run quicksort and collect frames
quicksort(arr, 0, len(arr) - 1, step=200)

# Animation
fig, ax = plt.subplots(figsize=(10, 5))
bar_rects = ax.bar(range(len(frames[0])), frames[0], color='skyblue', linewidth=0)
ax.set_title("Quick Sort Animation (Sampled, 10,000 numbers)")
ax.set_xlim(0, len(frames[0]))
ax.set_ylim(0, np.max(frames[0]) * 1.1)
ax.axis('off')

def update(frame):
    for rect, val in zip(bar_rects, frames[frame]):
        rect.set_height(val)
    ax.set_xlabel(f"Step {frame * 200}")
    return bar_rects

ani = animation.FuncAnimation(
    fig, update, frames=len(frames), interval=100, blit=False, repeat=False
)
plt.show()
