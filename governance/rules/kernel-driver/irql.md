# Kernel Driver IRQL Boundary

kernel-driver 變更必須宣告並保住所有被修改 dispatch、callback、與 cleanup path 的 callable IRQL 假設。

- 在可能高於 `PASSIVE_LEVEL` 的 context 中，不得執行 pageable、blocking、或 wait-based operation。
- 不要假設 callback 一定跑在 `PASSIVE_LEVEL`；contract 必須說清楚所需 IRQL，或明確 defer work。
- 任何碰到 ISR、DPC、completion、work-item、或 dispatch code 的 refactor，都必須保住 high-IRQL 與 passive-level work 之間的 handoff。
- 若 task 改變了 locking 或 callback flow，review evidence 必須說明為何 IRQL 行為仍然安全。
