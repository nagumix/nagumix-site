---
title: Getting Started
description: Install NaguMIX on Windows or run from source, then create your first composition.
weight: 20
---

## Install on Windows x64

[Download NaguMIX 0.5.0 setup](https://github.com/nagumix/nagumix/releases/download/v0.5.0/NaguMIX-0.5.0-windows-x64-setup.exe)
and run it for a per-user installation. The application and installers are
unsigned; Windows may show an unrecognized-app warning. You do not need Python.
The desktop shortcut is off by default.

Microsoft Visual C++ v14 Redistributable **x64 14.51.36247.0 or newer** is required.
Setup defaults to no elevation (`NoElevate=1`). If the runtime is missing or too
old, setup stops with guidance; ask an administrator to install the signed x64
runtime from Microsoft, then retry.

To explicitly permit setup's separate Microsoft runtime download and interactive
license/UAC prompts, run this from the download directory in PowerShell:

```powershell
.\NaguMIX-0.5.0-windows-x64-setup.exe NoElevate=0
```

NaguMIX still installs for the current user. See the
[versioned installation details](https://github.com/nagumix/nagumix/blob/v0.5.0/docs/WINDOWS_PACKAGING.md#optional-native-windows-installer).
Ordinary uninstall retains settings, images and the shared runtime.

For portable use, [download the ZIP](https://github.com/nagumix/nagumix/releases/download/v0.5.0/NaguMIX-0.5.0-windows-x64.zip),
extract the complete folder and run `NaguMIX.exe`, keeping all files together.
The same runtime is required. The [MSI and checksums]({{< relref "status.md" >}})
are also available; use the MSI only when the runtime is already present.

## Run from source

Source setup requires Git, Python 3.12, [uv](https://docs.astral.sh/uv/) and the
native runtime prerequisites for wxPython on your operating system. Follow the
[v0.5.0 application README](https://github.com/nagumix/nagumix/blob/v0.5.0/README.md#development-setup).

```console
git clone --branch v0.5.0 --depth 1 https://github.com/nagumix/nagumix.git
cd nagumix
uv sync --locked
uv run python main.py
```

NaguMIX normally opens fullscreen. Press **Esc** or **X** on the canvas to exit.

## Make your first canvas

The empty canvas shows **Drop images here**, with hints for adding images and
exiting. You can drop files anywhere on the canvas, including outside the border.
The notice disappears after the first successful image load and returns when
the canvas is empty again.

1. Drop image files onto the canvas, or right-click and choose **Add Images...**
   to select one or more files. With the canvas focused, the default shortcut is
   **Ctrl + O** on Windows/Linux or **Command + O** on macOS.
   Loading progress or errors appear on the canvas.
2. Click an image to select it, then drag to move it. Use **+** and **−** to zoom.
3. Drag the white handles to adjust the visible frame. For a cropped image,
   drag its small four-arrow grip to reposition the picture beneath the frame.
4. Open the context menu and choose **Save Canvas State...** to keep the layout,
   or **Export Canvas...** to create a still image.

A canvas state stores source paths and transforms, not copies of your images.
Keep the original files in place so the composition can be reopened.

## Make it comfortable

Open **Settings** to choose the appearance and configure navigation or arrangement.
Choose **Save** to apply changes; **Cancel**, Escape or closing the dialog discards
the draft. The Licensing page includes offline license texts.

Continue with [Controls & Workflow]({{< relref "workflow.md" >}}) for image browsing, GIF frames
and the difference between saving and exporting.

## Troubleshooting

### A saved layout cannot find its images

A saved canvas state records each source path; it does not embed a copy of the
image. If a source was moved or renamed, put it back at the recorded location
before loading the state again. NaguMIX does not currently offer automatic
relinking. A failed load leaves the current canvas in place.

### An image will not load

The canvas reports unsupported file types and decode failures. Check that the
file is a supported image, still exists, and opens normally in another image
viewer. A damaged file, an unsupported encoding inside a familiar extension or
a source that changed while it was being read may not decode. NaguMIX does not
repair source files.

The default Windows package has no HEIC/HEIF decoder. Installing Microsoft Store
codecs does not enable the optional Pillow decoder used in source environments.

### The mouse wheel does not browse nearby files

Select an image first, then check **Settings > Navigation > Mouse wheel
navigation**. When that setting is disabled, the plain vertical wheel does not
change files. **Ctrl + vertical wheel** remains the zoom gesture for the selected
image.

### Source startup stops before the window opens

Recheck the locked source setup and the native prerequisites for wxPython on
your operating system. On 64-bit Windows, NaguMIX also requires the current
Microsoft Visual C++ v14 Redistributable (x64); the startup warning provides the
Microsoft download and `winget` options when that runtime is missing. Platform
requirements can change, so use the
[application README](https://github.com/nagumix/nagumix/blob/v0.5.0/README.md#development-setup) as
the current setup reference.
