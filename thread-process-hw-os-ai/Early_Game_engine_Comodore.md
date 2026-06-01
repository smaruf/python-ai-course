The old-school graphics pipeline on machines like the Commodore 64 was radically different from a modern GPU.

## Commodore 64 Architecture

![Image](https://images.openai.com/static-rsc-4/KswflaF51qt12BteclteARm98s9P2LhnOO9DbWj_FkKuCXxp-IBXrU1ymHhe9ijpJJhbf49W9rve1-GVcE_0_6SCgUukxT1cZhGl-g3SL5-OWSX1TS03PneGa8SPVmSb6T9X9W9701BNXA9LNtyXPjSk-a7eZRafcbaJBtJcUexU-jvAbu3ctoFpIFGt8J3h?purpose=fullsize)

The main components were:

```text
+----------------+
| MOS 6510 CPU   |
| ~1 MHz         |
+----------------+
         |
         |
+----------------+
| RAM 64 KB      |
+----------------+
         |
         |
+----------------+
| VIC-II Video   |
| Chip           |
+----------------+
         |
         |
      TV Screen
```

Unlike modern PCs:

* No dedicated 3D GPU
* No shaders
* No vertex processing
* No texture units

The CPU did most of the game logic, while the VIC-II video chip read memory and generated the TV signal.

---

## Example: Moving a Spaceship

Suppose you are playing Uridium.

When you press RIGHT:

### Step 1: CPU Reads Joystick

```assembly
Read joystick port
```

CPU discovers:

```text
RIGHT pressed
```

---

### Step 2: CPU Updates Position

Game variables:

```text
ShipX = 100
ShipY = 50
```

CPU executes:

```text
ShipX = ShipX + 1
```

Now:

```text
ShipX = 101
```

---

### Step 3: CPU Updates Video Memory

The CPU writes new values into memory locations that the video chip will later read.

```text
RAM

Ship Sprite X = 101
Ship Sprite Y = 50
```

No rendering occurs yet.

The CPU simply changes bytes in RAM.

---

## How Pixels Appeared

The VIC-II chip continuously scanned memory.

Imagine a television drawing the screen line by line:

```text
Line 1
Line 2
Line 3
...
Line 200
```

About 50 or 60 times per second.

The VIC-II would read:

```text
Character memory
Sprite memory
Color memory
```

and convert them into a TV signal.

---

## Character Graphics

Many games didn't draw every pixel individually.

Instead, the screen was divided into tiles.

Example:

```text
+---+---+---+---+
| A | B | C | D |
+---+---+---+---+
| E | F | G | H |
+---+---+---+---+
```

Screen memory stored:

```text
65 66 67 68
69 70 71 72
```

which represented character patterns.

The VIC-II looked up the corresponding bitmap for each character and displayed it.

This saved enormous amounts of memory.

---

## Sprites: Early Hardware Graphics

One revolutionary feature of the C64 was hardware sprites.

A sprite is a small movable image.

Example:

```text
Player Ship

   /\
  /==\
 /====\
```

Stored as:

```text
Sprite Data
```

The CPU only needed to say:

```text
Sprite #0 X = 100
Sprite #0 Y = 50
```

The VIC-II handled drawing it.

This was one of the earliest forms of graphics acceleration.

---

## Without Sprites

If no sprite hardware existed:

```text
CPU
 |
 v
Draw every pixel manually
```

Very slow.

With sprites:

```text
CPU
 |
 v
Move sprite position
 |
 v
VIC-II draws sprite
```

Much faster.

---

## Example Memory Layout

Simplified:

```text
RAM

0x0400 -> Screen Characters
0xD800 -> Colors
0x2000 -> Sprite Data
```

CPU updates memory:

```assembly
LDA #100
STA SpriteX
```

VIC-II reads it later.

---

## The Raster Beam

Old TVs drew the screen using an electron beam.

```text
>>>>>>>>>>>>>>>>>
Line 1

>>>>>>>>>>>>>>>>>
Line 2

>>>>>>>>>>>>>>>>>
Line 3
```

The VIC-II had to feed pixels exactly when needed.

If the CPU changed memory while the beam was drawing:

```text
Screen glitches
```

could occur.

---

## Raster Interrupts

Advanced programmers synchronized with the TV beam.

```text
Wait until scan line 100
```

Then:

```text
Change colors
Move sprites
Switch graphics mode
```

This allowed visual tricks impossible on paper.

Many famous C64 demos relied on this.

---

## What Happened Every Frame?

A simplified game loop:

```text
1. Read joystick
2. Update game logic
3. Move enemies
4. Detect collisions
5. Update sprite positions
6. Wait for vertical blank
7. Repeat
```

The video chip generated the image independently.

---

## Comparison with Modern GPUs

| Commodore 64       | Modern GPU                 |
| ------------------ | -------------------------- |
| CPU ~1 MHz         | GPU ~2 GHz+                |
| 64 KB RAM          | 8–48+ GB VRAM              |
| 8 hardware sprites | Millions of polygons       |
| Character graphics | 3D meshes                  |
| VIC-II video chip  | Thousands of shader cores  |
| TV output          | HDMI/DisplayPort           |
| CPU updates memory | GPU runs graphics programs |

The fascinating part is that the core concept remains similar:

```text
Game Logic
      ↓
Update Graphics Data
      ↓
Video Hardware Reads Data
      ↓
Display Image
```

The difference is scale. A Commodore 64 might move a handful of sprites and tiles, while a modern GPU processes billions of pixels, triangles, and shader operations every second.
