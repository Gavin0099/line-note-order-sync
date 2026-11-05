# GL Hub Vendor Command Spec Truth

只要 task 涉及 GL Hub vendor command 的發送或實作，就必須先對照 spec truth layer，再決定這個動作是否有效。

- 發送 GL Hub vendor command 前，必須先確認所有必要前提都成立（chip、command issue mode、state、timing、data structure）。
- 不要因為 command 出現在 spec table 中，就假設它一定合法；spec 也定義了 ordering constraint、timing requirement、與 command table 本身看不出的 forbidden inference。
- 未確認 circuit design 前，不得硬編碼 I2C slave address（`SlvAddr`）。
- ISP 完成前，以及未等待 100ms 前，不得發送 `HW_RESET`。
- 不得在沒有前置 `Set VAL1=05` 的情況下發送 `Get VAL1=04`。
- 不得把 44-byte（`Set VAL1=04`）與 12-byte（`Set VAL1=05`）的 data structure 混用。
- 每個 GL Hub vendor command decision 都必須攜帶 `<rule_id>@<version>` 格式的 policy ref，且可追溯到 spec truth rule file。
