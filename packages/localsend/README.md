# localsend

Omarchy's Share menu sends files, folders and the clipboard with
`localsend --headless send`, and its Receive entry opens the LocalSend app, so
without this package the whole menu silently does nothing on the port.

Upstream omarchy-pkgs builds LocalSend from source with Flutter through fvm,
and Flutter publishes no Linux aarch64 SDK. This recipe instead packages the
release bundle the LocalSend project itself publishes for Linux arm64 (and
x86-64), pinned by checksum, in the same `/usr/lib/localsend` layout as the
source build. The bundle's binary already sets `RUNPATH` to its own `lib/`.
The separate LocalSend CLI is not included; Omarchy does not use it.
