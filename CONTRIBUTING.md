# Contributing

Start with BUILDING.md and run the regression suite. Keep package source pins and
checksums current, describe the exact hardware/runtime combination tested, and
separate compilation results from native hardware validation. Do not claim a
feature works because its package installs or a device enumerates.

For a pull request, explain the user-visible problem, the resulting behavior and
how you tested it. Preserve upstream notices. Avoid generic apt emulation,
disabling signature verification, or copying personal configuration into images.

Before posting logs, remove passwords, tokens, notebook URLs, SSH keys, private
hostnames, addresses, serial numbers and account information. Do not upload raw
inventory output: locally installed applications and container names can also
reveal private information. Report potential credential exposure privately using
GitHub's private vulnerability reporting when it is available.
