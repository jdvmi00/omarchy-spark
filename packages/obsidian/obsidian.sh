#!/bin/bash
# Omarchy Spark: run Obsidian with the Electron it ships, since Arch Linux ARM
# packages no Electron. Users may add permanent flags in
# ~/.config/obsidian/user-flags.conf, as with Arch's package.
OBSIDIAN_USER_FLAGS_FILE="${XDG_CONFIG_HOME:-$HOME/.config}/obsidian/user-flags.conf"
if [[ -f "${OBSIDIAN_USER_FLAGS_FILE}" ]]; then
   OBSIDIAN_USER_FLAGS=$(grep -v '^#' "$OBSIDIAN_USER_FLAGS_FILE")
fi
exec /usr/lib/obsidian/obsidian $OBSIDIAN_USER_FLAGS "$@"
