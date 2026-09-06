# Developer preview publication review

Reviewed for v0.1.0-preview.1 on 2026-09-06.

## Public scope

Source-only package recipes, local patches/helpers, source manifests and upstream
pins, regression tests, a regular-file image assembler, and developer documentation.
No installed-machine inventory, personal provisioning, disk writer, SSH material,
notebook tokens, device serials, vendor binaries or disk image is included.
The Omarchy keyring contains upstream public signing keys; its notices are retained.

## Checks completed

- Fresh exact-revision upstream test inputs fetched; both patch sets apply.
- All 19 host-side regression tests pass from the release checkout.
- All package recipes pass Bash syntax checks and generate `.SRCINFO` metadata.
- All 16 local recipe source hash entries match their checked-in inputs.
- Staged-file review found no known private machine identifiers, common credential
  patterns, unexpected binary payloads or oversized generated files.
- Local Markdown links checked, release scope and hardware claims reviewed.
- Upstream notices retained and a third-party provenance document added.
- CI runs the same regression suite with read-only repository permission and a
  pinned checkout action. No deployment or package installation runs in CI.

These checks are not an exhaustive security audit, legal clearance for binary
redistribution, a full clean build, or independent hardware replication. The
source-only publication avoids distributing the unreviewed vendor payloads.
See KNOWN-ISSUES.md and HARDWARE-VALIDATION.md for the remaining technical limits.
