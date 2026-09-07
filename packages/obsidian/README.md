# obsidian

Arch's `obsidian` recipe already supports aarch64 through Obsidian's arm64
tarball, but it runs the app with Arch's system Electron package, which Arch
Linux ARM does not have. This copy of the recipe (archlinux/packaging/packages/
obsidian at 9793f64d75f9505327ea1611b135c77aee0d3921) installs the whole
bundle under `/usr/lib/obsidian` and runs the Electron it ships. The launcher
keeps Arch's `~/.config/obsidian/user-flags.conf` convention. `pkgrel` carries
a `.1` suffix to mark the deviation.
