# ufw-docker

To fix the Docker and UFW security flaw without disabling iptables.

The recipe is omacom-io/omarchy-pkgs' `ufw-docker` PKGBUILD, unchanged, at the omarchy-pkgs
revision in upstream-lock.json. It is part of Omarchy's base package list and is
published upstream only in Omarchy's own repository, which the ARM port does not
use, so the port builds it from the pinned sources.
