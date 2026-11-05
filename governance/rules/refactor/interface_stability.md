# Refactor Interface Stability Rule Pack

- refactor work 必須保持 external contract 穩定，除非 task 已被明確改判為 behavior 或 interface change。
- public method signature、callback semantic、error surface、與 observable ordering 必須保持穩定，或有明確的 compatibility evidence 支撐。
- 若 compatibility 依賴 adapter、contract、或 characterization test，這些 test 就屬於 required refactor evidence，而不是可選文件。
