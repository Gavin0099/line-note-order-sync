# Refactor Boundary Safety Rule Pack

- refactor 不得在沒有明確 architecture approval 的情況下，引入新的 boundary crossing。
- 不要把 logic 跨 `Domain / Application / Adapter / Infrastructure` 邊界搬動，卻仍標記成 refactor。
- interface 或 dependency change 除非有 ADR 或明確 approval，否則必須保持既有 ownership、lifecycle、與 responsibility boundary。
- 若 refactor 的目的在於降低耦合，結果應讓 boundary 更清楚，而不是更隱性。
- 若無法確定變更屬於 structural 還是 behavioral，先 escalate，不要靜默擴 scope。
