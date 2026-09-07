# zed

Omarchy's Install → Editor → Zed adds `zed` and `omazed`. Arch builds Zed from
source for x86_64; Arch Linux ARM does not build it. Zed's own releases include
a complete Linux aarch64 bundle (cli, editor, private libraries, desktop entry
and icons), so this recipe packages that bundle, pinned by checksum, under
`/usr/lib/zed` with `/usr/bin/zed` linking to its cli.
