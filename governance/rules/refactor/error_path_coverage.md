# Error Path Coverage

## Rule ID
`REF-ERROR-001`

## Enforcement
`hard-stop`

## Requirement
refactor task 必須在變更前後都把 error-path behavior 顯性化：

- 在 pre-task planning 產出 `error_path_inventory`
- 在 post-task review 提交 `error_behavior_diff`
- 若有刻意的 behavior 變更，必須明確標記，讓 reviewer 能把它視為 behavior change，而不是 pure refactor

## `error_path_inventory` format
每個 error case 至少要包含：

- `error_id`: unique identifier
- `trigger`: 觸發此 error path 的條件
- `pre_refactor_behavior`: refactor 前的預期行為
- `affected_by_refactor`: `true` 或 `false`

## `error_behavior_diff` format
每個受影響的 error case 至少要包含：

- `error_id`: 對應回 inventory entry
- `pre_behavior`: refactor 前行為
- `post_behavior`: refactor 後行為
- `status`: `unchanged`、`changed`、或 `removed`
- `reviewer_note`: 當 `status` 不是 `unchanged` 時必填

## Hard-stop conditions
- 缺少 `error_path_inventory`
- 某個 `affected_by_refactor: true` 的 error case 沒有對應的 `error_behavior_diff`
- `status: changed` 或 `status: removed` 卻沒有 `reviewer_note`

## Scope boundary
這條規則只驗證結構與 reviewer-facing traceability。

- framework 只檢查 inventory 與 diff 是否存在、且內部一致
- framework **不會**證明 error-case 清單是否已完整列舉
- exhaustiveness 與 semantic correctness 仍屬 reviewer 與 testing 的責任
