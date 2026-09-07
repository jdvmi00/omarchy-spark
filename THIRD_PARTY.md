# Provenance and third-party material

The root MIT license covers original Omarchy Spark contributions, not downloaded
software or third-party material under another license. PKGBUILD `license` fields
describe the packaged software; they are not a grant to redistribute its binaries.

- Omarchy package recipes, installation helpers, keyring and patches derive from
  basecamp/omarchy and omacom-io/omarchy-pkgs. Their repository MIT notice is
  retained in LICENSES/Omarchy-MIT.txt. The keyring package identifies its payload
  as GPL-3.0-or-later; that license is also included. The public signing keyring
  contains public keys, not project credentials or private signing keys.
- The artwork under docs/media extends the Omarchy wordmark from basecamp/omarchy
  (MIT, notice retained): the letters s, p and k are new, drawn on the same
  15-pixel stair-step grid, and a and r reuse the original glyphs. Colors are the
  Tokyo Night theme values shipped with Omarchy. The lightning-bolt glyph and bracket icon
  are original. No NVIDIA logo or trademark artwork is used or imitated; the
  words NVIDIA and DGX Spark appear only as plain text naming the hardware.
- Kernel packaging derives from RageLtd/linux-dgx-spark; its MIT license remains
  in packages/linux-dgx-spark/LICENSE. Downloaded Linux/Ubuntu sources have their
  own kernel licenses. The included configuration is a build configuration.
- Aquamarine packaging preserves its upstream maintainer attribution; downloaded
  Aquamarine sources are BSD-3-Clause. GCC and CUDA packaging drew on Arch package
  recipes recorded in upstream-lock.json. GCC source and runtime exceptions apply
  to the resulting compiler. The CUDA glibc compatibility patch's source revision
  is documented in its package README and lock file.
- The ghostty recipe is Arch Linux's own packaging (archlinux/packaging/packages/
  ghostty, 0BSD) at the revision in upstream-lock.json, with documentation
  generation removed because Arch Linux ARM has no pandoc; it does not build
  that package itself.
- The archiso patch targets RageLtd/arch-dgx-spark-iso at the locked revision.
  The underlying repository is fetched for tests, not vendored or relicensed.
- graham33/nixos-dgx-spark and omacom/try-omarchy informed the port. They and all
  packaging reference revisions are credited in upstream-lock.json.
- NVIDIA CUDA, Nsight, AI Workbench, Dashboard and hotplug payloads are fetched
  from vendor URLs with recorded hashes. They are not included in this release.
  Their applicable licenses/EULAs and notices govern use and redistribution.
  This source-only preview makes no claim that binary/image redistribution is
  cleared, or that NVIDIA supports the modified platform.

No complete upstream checkout, vendor DEB, compiled package, disk image, firmware
or installed-machine inventory is included in the Git repository or release.
Public source URLs and immutable pins are retained for reproducibility and credit.

This document records provenance as the project understands it. It is not a
legal opinion, and the redistribution terms of each upstream payload were not
independently verified.
