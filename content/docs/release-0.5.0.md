---
title: NaguMIX 0.5.0
description: Windows x64 downloads, canvas removal and release limitations.
date: 2026-10-23
weight: 50
---

Released **23 October 2026**. NaguMIX 0.5.0 provides unsigned Windows x64 setup,
portable ZIP and MSI downloads. Start with [Availability]({{< relref "status.md" >}})
for exact downloads, matching source and checksums, then follow
[Getting Started]({{< relref "getting-started.md" >}}).

- **Delete** removes the selected canvas image and does nothing with no selection.
  Original image files stay unchanged; text fields keep normal Delete behavior.
- The borderless Windows canvas has a branded taskbar entry.
- Image drops and navigation ignore macOS AppleDouble metadata sidecars (`._*`).
- Packages include matching source, license notices and build manifests.
  No development Python installation is required.

Installation is per-user. Microsoft Visual C++ v14 Redistributable x64
14.51.36247.0 or newer is required; setup defaults to no elevation and stops with
guidance when the runtime is missing. See the getting-started guide for the
explicit interactive prerequisite route.

The default Windows package has no HEIC/HEIF decoder, HEVC implementation or
FFmpeg. Microsoft Store codecs do not enable the optional Pillow decoder path.
There are no macOS/Linux binaries or published WinGet package. Upgrade, offline
installation and reboot scenarios have not been validated. Intermittent
network-share provider failures remain undiagnosed.

The [public release record](https://github.com/nagumix/nagumix/releases/tag/v0.5.0)
contains the complete limits and acceptance notes. The packages match
[source v0.5.0](https://github.com/nagumix/nagumix/tree/v0.5.0), public commit
`9042605ebf08e124e87b24fc3dee48daef42de37` and source tree
`9469b22f98647228689bd92506f0c701657812d1`.
