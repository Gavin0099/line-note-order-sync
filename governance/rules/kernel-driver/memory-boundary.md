# Kernel Driver Memory Boundary

kernel-driver 變更必須把 user input、DMA buffer、與 mapped memory 視為 hostile boundary，而不是普通 C / C++ data。

- 在 dereference 或 copy 前，先驗證所有 buffer length、structure size、與 pointer 假設。
- 不得在沒有 explicit validation 的情況下信任 user-mode buffer、IOCTL payload、或外部提供的 length。
- 任何碰到 DMA、MDL、mapped view、或 shared memory 的變更，都必須保住 ownership、lifetime、與 cleanup symmetry。
- refactor 不得隱藏或削弱用來防止 use-after-free、double-free、stale mapping、或 memory-corruption risk 的檢查。
