# C# Threading Safety

- UI state change 必須發生在正確的 UI thread 或 dispatcher boundary。
- 除了明確的 event-handler boundary 之外，不要把 `async void` 當成可接受預設。
- 沒有同步策略的 cross-thread mutation，是 governance violation，不是 style issue。
- 只有在 async operation 確實需要 mutual exclusion 時，才使用可等待的同步機制；不得在持有 monitor / `lock` 時跨越 `await`。
- shared mutable state 必須明確說明所保護的 invariant 與 synchronization strategy；`volatile`、`Interlocked` 與 lock-based synchronization 不是可互換的通用修正。
