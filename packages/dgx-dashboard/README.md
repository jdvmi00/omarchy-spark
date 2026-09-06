# DGX Dashboard on Arch ARM

Experimental package matching the test machine’s installed version 0.25.11. The vendor
DEB URL and SHA256 were obtained from the Spark's APT metadata. Package files
are downloaded directly, with no vendor binaries committed here.

This translates Debian installation actions to Arch sysusers/tmpfiles and
package-owned system units. Service users cannot modify packaged binaries or
service definitions. The runtime notebook port map is service-writable. Service
startup is deliberately left to the eventual system integration step.

The package is not complete functional parity: authentication, notebook
environment creation, updates, and device settings require native-Arch testing.
In particular, Ubuntu-specific update operations need an Arch backend. Do not
represent successful packaging or binary loading as proof those functions work.

Binary paths and the original D-Bus policy are retained. The web service depends
on its admin service, and the vendor ports.env is the single port setting.

## Native Arch status backend (release 2)

The admin service has a private PATH containing adapters for its observed
`apt update`, `apt list --upgradable`, `apt dist-upgrade -s` and
`apt-cache show <candidate>` queries. They refresh a temporary pacman database,
read actual installed versions and repository metadata, and resolve a complete
transaction with pacman's print-only mode. No package is installed and the live
sync database is unchanged. The helpers are not on the host's normal PATH.

Inspect the full, timestamped result with:

```sh
sudo dgx-arch-package-status --refresh
```

The JSON includes held updates, the transaction preview, resolver warnings and
packages outside configured repositories. The latter need a port-managed source;
absence of repository updates is not proof those custom packages are current.
Successful results cache for at most 15 minutes. Refresh failures invalidate the
previous snapshot and return a nonzero status; unsupported operations fail.
The vendor UI can still collapse query errors into an empty package list, so the
JSON command's successful exit and timestamp are authoritative when diagnosing
update status. This remaining UI error-reporting limitation needs a frontend or
service API change, not a fabricated package record.

The vendor `UpdateAndReboot` method combines Ubuntu aptdaemon, firmware and reboot.
The package's D-Bus policy rejects that method until a native transaction and
rollback path is implemented. Firmware inventory remains available, but Dashboard
installation is unavailable; its current UI may offer the button and return
Access denied. No firmware has been flashed. This is an explicit incomplete
integration, not an Arch replacement for the full factory updater.

### Validation on 2026-09-06

- Native repository refresh and full transaction preview succeeded with zero
  pending repository updates. Fifteen locally built packages are inventoried.
- SHA256 of all four live sync databases stayed unchanged during the check.
- A separate vendor backend, on a private D-Bus and with a temporary credential
  store, parsed a synthetic update including epoch versions, description and size.
  `tests/check-dashboard-protocol.sh` reproduces that isolated protocol test.
- Production D-Bus inventory returns actual available firmware; the combined
  mutation method is denied before dispatch (tested with an invalid signature).
- Both services remain active, the web endpoint returns 200, and package integrity
  reports 51 files with zero changes. No failed system services.
- Unit tests cover query failures, version/held-package parsing, rejected writes,
  cache reuse and invalidation on refresh failure.

Native adapters follow the separate-database strategy described by
[checkupdates](https://man.archlinux.org/man/checkupdates.8.en), and the
[pacman print mode](https://man.archlinux.org/man/pacman.8.en) for transaction previews.
