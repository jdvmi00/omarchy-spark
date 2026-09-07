#!/bin/bash
# Build every recipe under packages/ from the committed tree alone, inside a
# fresh Arch Linux ARM container, in dependency order, feeding a local pacman
# repository so later recipes can depend on earlier ones.
#
#   scripts/clean-build.sh setup  [DIR]   create the container and its mount
#   scripts/clean-build.sh run    [DIR]   export HEAD, build everything, print the summary
#
# Run on an aarch64 Docker host (the Spark itself works). DIR defaults to
# ~/spark-port/clean-build and holds the source tarball, per-recipe logs,
# summary.txt and the resulting repo/. Nothing on the host is installed.
set -euo pipefail

dir=${2:-$HOME/spark-port/clean-build}
container=spark-clean-build
image=menci/archlinuxarm:latest
root=$(cd "$(dirname "$0")/.." && pwd)

order=(gcc15-dgx linux-dgx-spark omarchy-keyring omarchy-settings aquamarine-compat13 omarchy
       cuda-dgx-spark perftest dgx-spark-mlnx-hotplug nsight-dgx-spark nvidia-ai-workbench dgx-dashboard
       mise-bin xdg-terminal-exec ttfx aether cliamp herdr hyprland-preview-share-picker omacalc omacut
       omawrite omarchy-nvim tensaku tobi-try tzupdate ufw-docker yay localsend ghostty
       1password-cli 1password nordvpn-bin once-bin visual-studio-code-bin sublime-text-4 omarchy-emacs
       openai-codex-desktop voxtype-bin omazed zed bitwarden bitwarden-cli obsidian ollama)

setup() {
  mkdir -p "$dir/repo"
  docker rm -f "$container" >/dev/null 2>&1 || true
  docker run -d --name "$container" -v "$dir:/build" "$image" sleep infinity >/dev/null
  docker exec "$container" bash -euo pipefail -c '
    # pacman 7 cannot apply its Landlock download sandbox inside a container.
    sed -i "s/^\[options\]/[options]\nDisableSandbox/" /etc/pacman.conf
    pacman-key --init >/dev/null 2>&1; pacman-key --populate archlinuxarm >/dev/null 2>&1
    pacman -Syu --noconfirm >/dev/null
    pacman -S --noconfirm --needed base-devel git sudo >/dev/null
    useradd -m builder
    echo "builder ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/builder
    chown -R builder /build
    su builder -c "repo-add -q /build/repo/spark-local.db.tar.gz"
    printf "\n[spark-local]\nSigLevel = Optional TrustAll\nServer = file:///build/repo\n" >> /etc/pacman.conf
    pacman -Sy >/dev/null
    echo "container ready: $(uname -m), $(pacman -Q gcc | tr -d "\n")"'
}

run() {
  git -C "$root" archive --format=tar.gz -o "$dir/omarchy-spark-src.tar.gz" HEAD
  git -C "$root" rev-parse --short HEAD > "$dir/commit"
  docker exec -u builder "$container" bash -c '
    cd /build && rm -rf src && mkdir src && tar -xzf omarchy-spark-src.tar.gz -C src
    echo "commit $(cat commit) start $(date -Is)" > summary.txt
    for n in '"${order[*]}"'; do
      d=/build/src/packages/$n; [[ -d $d ]] || { echo "MISSING $n" >> summary.txt; continue; }
      start=$(date +%s)
      if (cd "$d" && makepkg -s --noconfirm --needed > "/build/log-$n.txt" 2>&1); then
        pkgs=$(ls "$d"/*.pkg.tar.*); cp $pkgs /build/repo/
        (cd /build/repo && repo-add -q spark-local.db.tar.gz $(basename -a $pkgs) >/dev/null 2>&1)
        sudo pacman -Sy >/dev/null 2>&1
        echo "PASS $n $(( $(date +%s) - start ))s $(basename -a $pkgs | tr "\n" " ")" >> summary.txt
      else
        echo "FAIL $n $(( $(date +%s) - start ))s $(grep -m1 -E "==> ERROR|error:" "/build/log-$n.txt" | cut -c1-140)" >> summary.txt
      fi
    done
    echo "DONE $(date -Is)" >> summary.txt'
  cat "$dir/summary.txt"
}

case ${1:-} in
  setup) setup ;;
  run) run ;;
  *) sed -n '2,12p' "$0"; exit 1 ;;
esac
