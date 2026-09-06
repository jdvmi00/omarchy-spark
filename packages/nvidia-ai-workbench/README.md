# NVIDIA AI Workbench on native Arch ARM

The vendor desktop and backend binaries are taken from the SHA512-pinned Spark
Debian package. Arch package release 2 removes group/world write permission from
the vendor payload. Release 4 adds native backend provisioning and scoped
compatibility helpers; it does not install an Ubuntu host or VM.

## Why the adapters exist

The vendor backend classifies Arch as unsupported. In that branch it skips GPU
and NVIDIA Container Toolkit detection and attempts Docker Desktop startup.
The vendor CLI also cannot manage background processes for that OS identifier.

The system service `nvwb-spark@<username>.service` runs the original backend as
that user. A private mount namespace supplies Ubuntu 24.04 metadata **only to
this service** so the existing Linux detection branch runs. A private PATH entry
translates the observed read-only `dpkg-query -Wf` request for
`nvidia-container-toolkit` into `pacman -Q`. Unrecognized package/query requests
fail. No apt implementation is installed, and the host's actual os-release file
is not changed. The service uses the native Arch libraries, driver and Docker.
Firmware and host package installation remain outside this adapter.

The CLI adapter handles readiness and shutdown only for the `local` context at
the user's default `~/.nvwb` directory. It checks the actual loopback API and
manages the corresponding system service. Other contexts and operations go to
the original vendor binary. Service start/stop uses `sudo -n systemctl` for that
specific unit; the bring-up account already has passwordless sudo. A production
installer must define the intended service-management authorization when it
removes the temporary bring-up sudo policy.

The helper `wb-svc` uses the real Docker Engine readiness check when the selected
runtime is Docker, and otherwise delegates to NVIDIA. The desktop's integrated
installer/updater still assumes Ubuntu; update this port through pacman.

## Configure

Required native components include Docker, NVIDIA Container Toolkit, git,
git-lfs, pciutils, sudo, Python and PyYAML. The service template currently requires
a home at `/home/<username>`. Configure Docker GPU access and add the account to
the docker group before running:

```sh
nvwb-spark-setup
```

Run as the user. Existing config, binaries/links and shell files are backed up
under `~/.nvwb/spark-backups`. The helper installs the vendor shell integration,
creates the local context when absent, and enables the user's system service.
Existing non-Docker configurations and conflicting local contexts require a
manual migration. `--no-start` configures without starting the service.

For an existing shell:

```sh
source ~/.local/share/nvwb/nvwb-wrapper.sh
nvwb activate local
nvwb -c local list projects
```

During transition from experimental release 3, stop and disable the previous
`systemctl --user` unit before starting the new system service. No project should
be building during that transition.

## Validation and limits

The CLI can list the environment catalog, create a project and build NVIDIA's
ARM64 CUDA 13.0 base. A project with one GPU starts JupyterLab, serves an
authenticated HTTP 200, and executes the CUDA unified-memory smoke test. All
three checks pass after a CLI-managed backend restart. The private compatibility
probe detects GB10, driver 610.57.04, toolkit 1.20.0 and the configured NVIDIA
Docker runtime. Evidence is recorded in [the hardware report](../../docs/HARDWARE-VALIDATION.md).
Release 5 normalizes only
the legacy CUDA/driver scalar version fields from `nvidia-smi -q
--display=COMPUTE`: NVIDIA 610 appends deprecation notes that the older Workbench
version parser mistakes for part of the number. Actual version values and other
commands are preserved. The adapter exists only in the service's private PATH.

The supplied tests check readiness failures, delegation of other contexts and
custom workbench directories, and truthful/read-only package-query behavior.
Desktop integration, third-party authentication, remote locations and automatic
vendor updates still require separate validation.
