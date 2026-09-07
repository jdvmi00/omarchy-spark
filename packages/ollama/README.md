# ollama and ollama-cuda

Omarchy's Install → AI → Ollama installs `ollama-cuda` when `nvidia-smi` is
present. Arch's recipe is x86_64-only because Arch's CUDA is; Arch Linux ARM
has neither. This is Arch's split recipe adapted for the Spark: the CPU package
`ollama` and a `ollama-cuda` backend built only for the GB10 (compute
capability 12.1) against the port's CUDA 13 toolkit under `/usr/local/cuda`,
with GCC 15 as the CUDA host compiler, as the port's perftest recipe does. The
ROCm, Vulkan and docs packages are dropped. The source is pinned to the
v0.33.3 commit; the service, sysusers, tmpfiles and ld.so.conf files are Arch's.
