# ghostty

Omarchy's Install → Terminal → Ghostty runs `omarchy-pkg-add ghostty`, which
fails on the port with "target not found" because Arch Linux ARM does not
build Ghostty. Arch's own recipe declares aarch64 and needs only Zig and a few
build tools that Arch Linux ARM provides, so the port carries that recipe with
one change, from archlinux/packaging/packages/ghostty at commit
`7c601d97c8e447371dbc004368b3b83666b61225` (recorded in upstream-lock.json).

The one change: Arch builds Ghostty's man pages and HTML documentation with
pandoc, which Arch Linux ARM does not carry, so the port drops `-Demit-docs`
and the `pandoc-cli` build dependency. The terminal is complete; only its
offline documentation is missing. `pkgrel` carries a `.1` suffix to mark the
deviation from Arch's release.

A second change: Ghostty 1.3.1 requires Zig 0.15.2, and Arch Linux ARM's `zig`
package is already 0.16, whose dependency cache the build cannot read. The recipe
therefore fetches the pinned Zig 0.15.2 release from ziglang.org for the build,
as the port's herdr recipe does, instead of depending on the repository's `zig`.
