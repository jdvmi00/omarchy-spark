# Aquamarine ABI 13 runtime

Observed Arch ARM repository state on 2026-09-05: Hyprland 0.56.1 and
hyprtoolkit 0.5.4 require libaquamarine.so.13, while aquamarine 0.15.0 provides
libaquamarine.so.14. Pacman cannot resolve the desktop transaction as published.

This package builds the pinned upstream Arch recipe for Aquamarine 0.14.0 and
installs only its versioned ABI 13 libraries. Headers, pkg-config files and the
unversioned linker name stay owned by the current aquamarine package. Both can
coexist without downgrading the repository's current package or faking an ABI.

Native ARM compilation passed; readelf confirms SONAME libaquamarine.so.13,
ldd resolves its dependencies, and the previously failing desktop package
transaction now resolves. Graphical runtime compatibility still needs a booted
Spark test. Remove this compatibility package once installed consumers no longer
require ABI 13; do not leave it as a substitute for coherent future updates.
