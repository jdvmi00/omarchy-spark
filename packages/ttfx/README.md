# ttfx

Omarchy's screensaver renderer: a single static Rust binary that plays text
effects in the terminal. `omarchy-launch-screensaver` exits silently when it is
missing, so without this package neither the idle timer nor the menu entry
starts the screensaver.

The recipe is omacom-io/omarchy-pkgs' `ttfx` PKGBUILD, unchanged. Upstream
publishes the package only in Omarchy's own x86_64/aarch64 repository, which
the ARM port does not use, so it is built here from the pinned source tarball.
It needs `rust` at build time and nothing beyond glibc and gcc-libs at runtime.
