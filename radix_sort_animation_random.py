import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Generate 10,000 random numbers
arr = np.random.randint(0, 100000, size=10000)
frames = []

def counting_sort(arr, exp):
    n = len(arr)
    output = [0] * n
    count = [0] * 10

    for i in range(n):
        index = arr[i] // exp
        count[index % 10] += 1

    for i in range(1, 10):
        count[i] += count[i - 1]

    for i in range(n - 1, -1, -1):
        index = arr[i] // exp
        output[count[index % 10] - 1] = arr[i]
        count[index % 10] -= 1

    for i in range(n):
        arr[i] = output[i]

def radix_sort_collect_frames(arr, step=200):
    arr = arr.copy()
    max_num = max(arr)
    exp = 1
    frames.append(arr.copy())
    while max_num // exp > 0:
        counting_sort(arr, exp)
        if len(frames) == 0 or len(frames) % step == 0:
            frames.append(arr.copy())
        exp *= 10
    frames.append(arr.copy())

# Run radix sort and collect frames
radix_sort_collect_frames(arr, step=200)

# Animation
fig, ax = plt.subplots(figsize=(10, 5))
bar_rects = ax.bar(range(len(frames[0])), frames[0], color='skyblue', linewidth=0)
ax.set_title("Radix Sort Animation (Sampled, 10,000 numbers)")
ax.set_xlim(0, len(frames[0]))
ax.set_ylim(0, np.max(frames[0]) * 1.1)
ax.axis('off')

def update(frame):
    for rect, val in zip(bar_rects, frames[frame]):
        rect.set_height(val)
    ax.set_xlabel(f"Step {frame * 200}")
    return bar_rects

# interval is in milliseconds (e.g. 200 = 0.2 seconds)
ani = animation.FuncAnimation(
    fig, update, frames=len(frames), interval=200, blit=False, repeat=False
)
plt.show()
