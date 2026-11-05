# Refactor No Partial Cleanup Rule Pack

- refactor work 不得在 exception 或中途失敗路徑中留下 partial side effect 或 half-cleaned resource。
- 當 refactor 牽涉 resource ownership 或 multi-step operation 時，必須對 cleanup、rollback、dispose、release、或 revert behavior 提供 evidence。
- 如果 refactor 保住了 happy path，卻削弱 failure cleanup，就不能視為安全。
