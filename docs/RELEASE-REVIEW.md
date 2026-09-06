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
  pinned checkout action. No deployment or port package installation runs in
  CI; the workflow installs only PyYAML when the runner lacks it.

These checks are not an exhaustive security audit, legal clearance for binary
redistribution, a full clean build, or independent hardware replication. The
source-only publication avoids distributing the unreviewed vendor payloads.
See KNOWN-ISSUES.md and HARDWARE-VALIDATION.md for the remaining technical limits.

## Post-publication readiness reassessment (2026-09-06)

An independent offline review of the published commit 513d2959 found no
confirmed security vulnerability in the tracked source. Its coverage was
explicitly partial: the large kernel configuration was not audited option by
option, and vendor/upstream payloads and the installed machine were out of
scope. Its verdict was a sanitized experimental source release, not an
independently reproducible, finished or certified-clean port. Disposition of
its items in the main branch:

| Review item | Disposition |
| --- | --- |
| `omarchy-settings` scriptlet overwrote administrator `/etc` files on every upgrade | Corrected in 4.0.2-4: local edits are kept and packaged content lands as `.pacnew`. Host-side tests; the upgrade on the test Spark left every live file untouched |
| `nvwb-spark-setup` changed config and links before detecting a conflicting local context | Corrected in 0.169.2.16-6: all checks precede any write; global `daemon-reload` removed. Host-side tests; re-run on the test Spark without changes |
| `make-disk-image.py` could overwrite or alias its manifest sidecar | Corrected: `.json` image names are refused and the sidecar is created exclusively. Tested |
| `check-jupyter-runtime.py` accepted any HTML 200, including a login page | Corrected: authenticated contents/status API checks, no redirects, no-token and wrong-token refusals required. Tested against a stub server; passed inside the project container on the test Spark before and after a backend restart |
| Workbench privileges, global `daemon-reload`, fixed port and single-user scope undocumented | Documented in the package README with an example sudoers rule; no policy is installed |
| No clean-chroot build or independent hardware installation; update/rollback unfinished | Clean container build of all 28 recipes passed on 2026-09-06 (`manifests/clean-build-2026-09-06.json`); second-machine installation and update/rollback still outstanding |
| Provenance notes are not a legal opinion | Stated in THIRD_PARTY.md |

The regression suite is a host-side check of this repository's helpers and
patches. Passing it does not certify the operating system, the vendor payloads
or any installed machine. The source-only experimental label stays until a
fresh ARM clean build and a second-machine installation have been reproduced.
The review produced no evidence of a security incident or credential leak.
