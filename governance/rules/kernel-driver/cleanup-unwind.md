# Kernel Driver Cleanup And Unwind

kernel-driver code 必須在 partial initialization、failure path、unload、remove、與 cancel flow 中維持對稱的 unwind 行為。

- 若 initialization 只成功到一半，failure path 必須釋放所有已取得的 resource。
- unload、device-remove、surprise-remove、與 cancel path 必須被視為 first-class behavior，而不是 best-effort cleanup。
- refactor 必須保住 rollback order、object ownership、與 lock-release symmetry。
- review evidence 應說明 halfway failure、cleanup、與 teardown 在變更後為何仍然安全。
