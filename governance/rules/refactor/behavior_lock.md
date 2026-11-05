# Refactor Behavior Lock Rule Pack

- 只有在可觀測行為保持不變時，才可視為純 refactor。
- 測試必須鎖住 expected behavior，而不只是 implementation detail。
- refactor 後的綠燈測試，只有在包含 regression、boundary、與 failure-path coverage 時，才算有效 evidence。
- 若行為被刻意改變，這就不再是 pure refactor，必須改按 feature 或 behavior change 處理。
- 若行為尚未先被鎖定，不能只靠 readability 來合理化高風險 refactor。
