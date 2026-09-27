---
title: Controls & Workflow
description: Arrange images, choose GIF frames and save or export your canvas.
weight: 30
---

## Arrange and reframe

Drop still images or GIF files anywhere on the canvas, or right-click and choose
**Add Images...** to select one or more files. With the canvas focused, the
default shortcut is **Ctrl + O** on Windows/Linux or **Command + O** on macOS.
You can add files to an empty canvas or an existing composition.
PNG, JPEG, AVIF and HEIC/HEIF are among the supported input formats.

Click an image to select it and drag to move it. White handles resize its visible
frame while keeping the image scale fixed. When a smaller frame hides part of the
image, hover inside it and drag the four-arrow grip to move the image beneath it.
These edits do not modify the original file.

Use **+**, **−** or **Ctrl + vertical mouse wheel** to zoom the selected image.
An explicit zoom restores the full frame first. The context menu also offers
duplicate, delete, reset, mark-and-swap and whole-canvas arrangement commands.

## Browse and choose a frame

The vertical mouse wheel navigates neighboring files when wheel navigation is
enabled. Settings controls sorting and preload behavior.

Animated GIFs start paused. Select a GIF and press **Space** to play or pause,
or **,** and **.** to step backward and forward. Hover controls also provide
frame navigation, playback and a timeline for seeking.

## Save or export

**Save Canvas State** writes a JSON layout referencing the source files and their
transforms, including the displayed frame of an animated GIF. It does not embed
the images. When loading a state, the current canvas remains in place until all
referenced sources have decoded successfully.

**Export Canvas** produces a still PNG, JPEG, WebP or BMP. Use this for a finished
composition, including the GIF frames currently shown; use a saved state when
you want to keep editing the layout.
Saving and export replace the destination only after successful completion.

## Keyboard reference

| Input | Action |
| --- | --- |
| Esc or X on the canvas | Exit |
| Ctrl + O on Windows/Linux; Command + O on macOS (canvas focused) | Add Images... (default shortcut) |
| + / − | Zoom selected image |
| Ctrl + vertical wheel | Zoom selected image |
| Vertical wheel | Navigate files when enabled |
| , / . | Previous / next GIF frame |
| Space | Toggle the selected GIF or focused control |

For your first composition, follow [Getting Started]({{< relref "getting-started.md" >}}).
