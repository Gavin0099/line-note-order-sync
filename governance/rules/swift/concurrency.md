# Swift Concurrency Boundary

- 會影響 UI 的 state 必須尊重正確的 actor 或 main-thread boundary。
- 不要把 callback-style side effect 與 structured concurrency 混在一起，導致 ownership 或 cancellation 變得模糊。
- task cancellation 與 error propagation 必須在 boundary 上保持明確。
