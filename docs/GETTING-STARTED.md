# Getting started with Omarchy Spark

Omarchy Spark brings native Arch Linux ARM and Omarchy to NVIDIA DGX Spark,
with integration for CUDA, GPU containers, AI Workbench and DGX Dashboard.
The current release is for developers helping reproduce and complete the port.

## Explore or contribute from another Linux machine

You do not need a Spark to inspect the recipes or run host regression tests.
Install Python 3.11 or newer, PyYAML, Git, Bash and patch using your distribution's
package manager. In a fresh directory:

```sh
git clone --branch v0.1.0-preview.3 https://github.com/jdvmi00/omarchy-spark.git
cd omarchy-spark
python3 scripts/prepare-test-sources.py
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

The preparation step downloads pinned upstream test sources and applies the
port patches. Run it once per fresh checkout; it refuses existing test-source
directories. The test suite uses temporary files and command stubs. It does not
install the port or verify NVIDIA hardware. Create a branch before making changes.

## Build on ARM64

Follow [BUILDING.md](../BUILDING.md) in a disposable Arch Linux ARM environment.
Read each recipe and its package-specific instructions. The tested driver set
and the gap in pinning all rolling dependencies are documented there.
A package build inside DGX OS does not establish native Arch boot compatibility.

## Install on a Spark

There is no supported end-to-end installation procedure or downloadable boot
image yet. The successful test installation was manually integrated on an
external SSD. This repository does not reproduce that machine in one command;
do not interpret the image assembly utility as an installer.

Review [known issues](KNOWN-ISSUES.md) and [hardware validation](HARDWARE-VALIDATION.md)
before planning an experimental installation. Keep DGX OS and a working recovery
path. A tested installation, update and rollback procedure is a release requirement.

## Help complete the port

The most valuable next contributions are a recorded clean ARM64 build, a
reproducible external-drive installation, and verification on an independent
Spark. See [release criteria](RELEASE-CRITERIA.md) and
[contributing](../CONTRIBUTING.md). Report exact versions and distinguish device
detection, package installation and actual workload execution. Share sanitized
results, not raw inventories or credentials.
