A **GPU (Graphics Processing Unit)** was originally designed to render graphics, but it turns out that the same architecture is excellent for many scientific and AI workloads because it can perform **many calculations in parallel**.

## The Core Difference

A CPU is optimized for:

* Low latency
* Complex branching logic
* Running operating systems and applications

A GPU is optimized for:

* High throughput
* Massive parallelism
* Performing the same operation on many pieces of data simultaneously

### CPU

```text
+------+ +------+ +------+ +------+
|Core 1| |Core 2| |Core 3| |Core 4|
+------+ +------+ +------+ +------+
```

A few powerful cores.

### GPU

```text
+--+--+--+--+--+--+--+--+
|C |C |C |C |C |C |C |C |
+--+--+--+--+--+--+--+--+
|C |C |C |C |C |C |C |C |
+--+--+--+--+--+--+--+--+
|C |C |C |C |C |C |C |C |
+--+--+--+--+--+--+--+--+
```

Thousands of smaller compute units.

---

## How GPUs Were Originally Used

Suppose you're rendering a game at:

```text
1920 × 1080
```

That's over 2 million pixels.

For each pixel, the GPU computes:

* Color
* Lighting
* Shadows
* Reflections
* Texture mapping

Since each pixel can be processed independently, the GPU assigns different pixels to different cores.

```text
Pixel 1  → Core A
Pixel 2  → Core B
Pixel 3  → Core C
...
```

Millions of operations happen simultaneously.

---

## GPU Architecture

A modern GPU consists of:

```text
+----------------------+
| GPU                  |
|                      |
| +------------------+ |
| | Compute Units    | |
| +------------------+ |
| | Compute Units    | |
| +------------------+ |
| | Compute Units    | |
| +------------------+ |
|                      |
| Shared Memory       |
| Cache               |
+----------------------+
```

For example, an NVIDIA GPU contains many Streaming Multiprocessors (SMs), each with dozens or hundreds of arithmetic units.

---

## Threads and Warps

GPUs execute work as thousands of threads.

Example:

```cpp
for each pixel:
    color = calculate(pixel)
```

Instead of one CPU thread:

```text
CPU:
Thread 1
Thread 2
Thread 3
```

The GPU may launch:

```text
Thread 1
Thread 2
...
Thread 1000000
```

These are grouped into "warps" (on NVIDIA GPUs typically 32 threads).

```text
Warp 1: Threads 1-32
Warp 2: Threads 33-64
Warp 3: Threads 65-96
```

A warp executes the same instruction at the same time on different data.

This is called **SIMT (Single Instruction, Multiple Threads)**.

---

## Memory Hierarchy

GPU memory is organized in layers.

```text
Registers (fastest)
      ↓
Shared Memory
      ↓
L1 Cache
      ↓
L2 Cache
      ↓
VRAM (GDDR/HBM)
```

VRAM stores:

* Textures
* AI model weights
* Training data
* Matrices

Modern AI GPUs may have tens or hundreds of GB of high-bandwidth memory.

---

## Example: Matrix Multiplication

Consider:

```text
A(1000×1000)
×
B(1000×1000)
```

Each output element can be computed independently.

```text
Output[0][0] → Thread 1
Output[0][1] → Thread 2
Output[0][2] → Thread 3
...
```

Thousands of GPU cores work simultaneously.

This is why GPUs became dominant for deep learning.

---

## AI Workloads

A neural network layer often performs:

```text
Y = W × X + B
```

where W and X are large matrices.

GPUs excel because they can compute many elements of Y at the same time.

For modern AI models:

```text
Prompt
  ↓
Embeddings
  ↓
Attention
  ↓
Feed Forward Layers
  ↓
Output
```

Most of the work is matrix math, which maps perfectly to GPU hardware.

---

## GPU vs TPU

| Feature         | GPU                                                                                                                                                               | TPU                                                               |
| --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| Purpose         | General parallel computing                                                                                                                                        | AI-specific computing                                             |
| Flexibility     | Very high                                                                                                                                                         | Lower                                                             |
| Graphics        | Yes                                                                                                                                                               | No                                                                |
| AI Training     | Excellent                                                                                                                                                         | Excellent                                                         |
| AI Inference    | Excellent                                                                                                                                                         | Excellent                                                         |
| Architecture    | Many programmable cores                                                                                                                                           | Large systolic arrays                                             |
| Vendor Examples | [NVIDIA](https://www.nvidia.com?utm_source=chatgpt.com), [AMD](https://www.amd.com?utm_source=chatgpt.com), [Intel](https://www.intel.com?utm_source=chatgpt.com) | [Google TPU](https://cloud.google.com/tpu?utm_source=chatgpt.com) |

## Details of GPU:

If we focus on the **original purpose of a GPU—drawing images on a display**—the process is fascinating because the GPU converts a 3D scene into millions of colored pixels many times per second.

## High-Level Pipeline

```text
Game/Application
       |
       v
    CPU
       |
       v
     GPU
       |
       v
 Frame Buffer
       |
       v
 Display Controller
       |
       v
   Monitor
```

For a 1920×1080 display running at 60 Hz:

```text
1920 × 1080 = 2,073,600 pixels
```

The GPU must generate:

```text
2,073,600 × 60
=
124,416,000 pixels/second
```

---

## Step 1: CPU Creates Scene

Suppose a game contains:

* A car
* A road
* Buildings
* Trees

The CPU:

* Updates game logic
* Handles keyboard/mouse input
* Computes physics
* Determines object positions

Then it sends drawing commands to the GPU.

Example:

```text
Draw Car Mesh
Draw Road Mesh
Draw Building Mesh
Draw Tree Mesh
```

---

## Step 2: Geometry Data

Objects are represented as triangles.

A car model may contain:

```text
50,000 triangles
```

Each triangle consists of vertices:

```text
Vertex:
x, y, z
normal
texture coordinates
color
```

Example:

```text
Triangle

V1(x1,y1,z1)
V2(x2,y2,z2)
V3(x3,y3,z3)
```

Modern GPUs are optimized to process billions of triangles per second.

---

## Step 3: Vertex Shader

The first major programmable stage is the vertex shader.

Input:

```text
Vertex Position
```

Output:

```text
Screen Position
```

The GPU transforms 3D coordinates into camera space.

```text
World Space
      ↓
View Space
      ↓
Projection Space
      ↓
Screen Space
```

Mathematically:

```text
Vertex'
=
Projection × View × Model × Vertex
```

This uses matrix multiplication extensively.

Each vertex can be processed independently, making it ideal for parallel execution.

---

## Step 4: Primitive Assembly

Vertices are grouped into triangles.

Example:

```text
V1
V2
V3
```

becomes:

```text
Triangle #1
```

The GPU determines which triangles are visible.

Invisible triangles may be discarded.

---

## Step 5: Clipping

Anything outside the camera view is removed.

Example:

```text
Camera View

+----------+
| Visible  |
| Region   |
+----------+
```

If part of a triangle lies outside:

```text
Outside Part -> Removed
Inside Part -> Kept
```

This saves processing power.

---

## Step 6: Rasterization

This is where 3D geometry becomes pixels.

Example triangle:

```text
   /\
  /  \
 /____\
```

Rasterizer determines:

```text
Which pixels belong to this triangle?
```

Result:

```text
Pixel 101
Pixel 102
Pixel 103
...
```

Millions of pixels can be generated simultaneously.

---

## Step 7: Fragment (Pixel) Shader

Each generated pixel runs a small program.

Input:

```text
Position
Texture
Lighting Data
Normal Vector
```

Example:

```glsl
color = texture(textureMap, uv)
```

The shader may calculate:

* Color
* Lighting
* Reflection
* Transparency
* Shadows

Example lighting equation:

```text
Final Color =
Texture Color × Light Intensity
```

Modern games may execute billions of shader operations every second.

---

## Step 8: Texture Sampling

Textures are images stored in GPU memory.

Examples:

* Brick wall texture
* Grass texture
* Car paint texture

The pixel shader fetches texture data.

```text
Texture Memory
      ↓
Pixel Shader
      ↓
Pixel Color
```

A single frame can require millions of texture reads.

---

## Step 9: Depth Testing (Z-Buffer)

The GPU must determine which object is in front.

Example:

```text
Car
Behind
Wall
```

Both may project onto the same screen pixel.

The GPU stores depth values:

```text
Pixel 100:
Car Depth = 5
Wall Depth = 10
```

Since 5 is closer:

```text
Display Car Pixel
Discard Wall Pixel
```

This is handled by the Z-buffer.

---

## Step 10: Blending

For transparency:

```text
Glass Window
```

The GPU combines colors.

Example:

```text
Final =
70% Window +
30% Background
```

This creates transparent effects.

---

## Step 11: Frame Buffer

The final image is written into memory called the frame buffer.

Example:

```text
Frame Buffer

Pixel 1 -> RGB
Pixel 2 -> RGB
Pixel 3 -> RGB
...
```

For 1920×1080:

```text
2,073,600 pixels
```

Each pixel may use:

```text
32 bits (RGBA)
```

One frame:

```text
≈ 8 MB
```

---

## Step 12: Display Engine

The GPU contains dedicated display hardware.

```text
Frame Buffer
      ↓
Display Controller
      ↓
HDMI / DisplayPort
      ↓
Monitor
```

The controller continuously scans memory:

```text
Row 1
Row 2
Row 3
...
```

and sends pixel values to the monitor.

---

## Double Buffering

To avoid flickering:

```text
Front Buffer
Back Buffer
```

Current frame:

```text
Front Buffer
```

GPU renders next frame:

```text
Back Buffer
```

When complete:

```text
Swap Buffers
```

This produces smooth animation.

---

## What Happens at 144 FPS?

For:

```text
2560 × 1440
144 Hz
```

GPU may process:

```text
530 million+
pixels per second
```

along with:

* Geometry calculations
* Texture sampling
* Shadow generation
* Anti-aliasing
* Ray tracing (modern GPUs)

This is why GPUs contain thousands of arithmetic units, specialized texture units, rasterizers, caches, memory controllers, display engines, and video encoders.

### Simplified Internal Architecture

```text
              CPU Commands
                     |
                     v
        +----------------------+
        | Command Processor    |
        +----------------------+
                     |
                     v
        +----------------------+
        | Vertex Shaders       |
        +----------------------+
                     |
                     v
        +----------------------+
        | Rasterizer           |
        +----------------------+
                     |
                     v
        +----------------------+
        | Pixel Shaders        |
        +----------------------+
                     |
                     v
        +----------------------+
        | Depth/Blend Units    |
        +----------------------+
                     |
                     v
        +----------------------+
        | Frame Buffer         |
        +----------------------+
                     |
                     v
        HDMI / DisplayPort
                     |
                     v
                Monitor
```

This pipeline—from vertices → triangles → pixels → frame buffer → monitor—is the fundamental mechanism that has powered real-time computer graphics for decades, with modern APIs like DirectX, OpenGL, and Vulkan exposing it to developers.

### Simplified Analogy

Imagine calculating the salaries of 1 million employees:

* **CPU**: A few expert accountants working very fast.
* **GPU**: Thousands of accountants each handling a small subset.
* **TPU**: A factory built specifically for salary calculations, extremely fast but less flexible.

That's why CPUs run your operating system, GPUs power games and AI, and TPUs are specialized accelerators for large-scale machine learning.
