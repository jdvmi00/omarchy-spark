#!/usr/bin/env python3
"""Read-only initial DGX Spark inventory; standard library only."""

import gzip
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys


def capture(argv):
    if not shutil.which(argv[0]):
        return {"status": "unavailable"}
    try:
        result = subprocess.run(
            argv, capture_output=True, text=True, timeout=20,
            env={**os.environ, "LC_ALL": "C", "SYSTEMD_PAGER": "cat"},
        )
        return {"status": "ok" if result.returncode == 0 else "error",
                "returncode": result.returncode,
                "stdout": result.stdout, "stderr": result.stderr}
    except subprocess.TimeoutExpired:
        return {"status": "timeout"}
    except OSError as exc:
        return {"status": "error", "error": str(exc)}


def kernel_config():
    candidates = [Path("/proc/config.gz"),
                  Path("/boot") / ("config-" + platform.release())]
    for path in candidates:
        try:
            if path.suffix == ".gz":
                with gzip.open(path, "rt") as stream:
                    content = stream.read()
            else:
                content = path.read_text()
            return {"status": "ok", "source": str(path), "content": content}
        except (OSError, UnicodeError):
            continue
    return {"status": "unavailable"}


def main():
    if platform.system() != "Linux" or not shutil.which("dpkg-query"):
        print("Run this collector on the Spark's existing DGX OS installation.",
              file=sys.stderr)
        return 2
    commands = {
        "packages": ["dpkg-query", "-W", "-f",
                     "${binary:Package}\t${Version}\t${Architecture}\t${db:Status-Status}\t${source:Package}\t${source:Version}\n"],
        "manual_packages": ["apt-mark", "showmanual"],
        "held_packages": ["apt-mark", "showhold"],
        "service_units": ["systemctl", "list-unit-files", "--type=service",
                          "--no-pager", "--no-legend"],
        "timer_units": ["systemctl", "list-unit-files", "--type=timer",
                        "--no-pager", "--no-legend"],
        "pci_devices": ["lspci", "-nnk"],
        "kernel_modules": ["lsmod"],
        "gpu": ["nvidia-smi", "--query-gpu=name,driver_version,memory.total",
                "--format=csv,noheader"],
        "cuda_compiler": [shutil.which("nvcc") or "/usr/local/cuda/bin/nvcc", "--version"],
        "container_toolkit": ["nvidia-ctk", "--version"],
        "container_cli": ["nvidia-container-cli", "--version"],
        "docker_version": ["docker", "--version"],
        "container_images": ["docker", "image", "ls", "--digests", "--no-trunc",
                             "--format", "{{json .}}"],
    }
    try:
        os_release = Path("/etc/os-release").read_text()
    except OSError:
        os_release = None
    report = {
        "schema_version": 1,
        "architecture": platform.machine(),
        "kernel_release": platform.release(),
        "page_size": os.sysconf("SC_PAGE_SIZE"),
        "os_release": os_release,
        "kernel_config": kernel_config(),
        "checks": {name: capture(argv) for name, argv in commands.items()},
    }
    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
