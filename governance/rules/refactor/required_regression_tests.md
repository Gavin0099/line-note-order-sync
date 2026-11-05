# Refactor Required Regression Tests Rule Pack

- refactor work 必須提供 regression evidence，不能只丟一份 passing test summary。
- 可接受的訊號包括：regression test、characterization test、behavior-lock test、或能保住可觀測行為的 contract test。
- 若沒有可辨識、明確指向 regression 的 evidence，只說「tests passed」不足以支撐高信心 refactor approval。
