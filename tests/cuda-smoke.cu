#include <cuda_runtime.h>
#include <cstdio>

#define CUDA_OK(expr) do { \
    cudaError_t err = (expr); \
    if (err != cudaSuccess) { \
        std::fprintf(stderr, "%s: %s\n", #expr, cudaGetErrorString(err)); \
        return 1; \
    } \
} while (0)

__global__ void fill(int* values, int count) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < count) values[i] = i * 3 + 7;
}

int main() {
    constexpr int count = 1 << 20;
    int* values = nullptr;
    CUDA_OK(cudaMallocManaged(&values, count * sizeof(int)));
    fill<<<(count + 255) / 256, 256>>>(values, count);
    CUDA_OK(cudaGetLastError());
    CUDA_OK(cudaDeviceSynchronize());
    for (int i = 0; i < count; ++i) {
        if (values[i] != i * 3 + 7) {
            std::fprintf(stderr, "Result mismatch at index %d\n", i);
            cudaFree(values);
            return 1;
        }
    }
    CUDA_OK(cudaFree(values));
    std::puts("PASS: CUDA kernel execution and CPU verification of 4 MiB unified memory");
    return 0;
}
