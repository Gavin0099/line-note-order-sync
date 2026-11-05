# Avalonia UI Thread

- UI control mutation 與 `PropertyChanged` side effect 必須在 `Dispatcher.UIThread` 或等價的安全邊界上執行。
- ViewModel 不應把跨 thread 的 UI 修補邏輯藏成 convenience shortcut。
- 若某條流程依賴 UI-thread affinity，測試應把這個依賴顯性化。
- Avalonia control 的讀寫必須留在 UI thread；從 background thread 進入時，應透過適當的 dispatcher boundary。
- 只有在不需要等待完成或取得結果時，才使用 `Dispatcher.UIThread.Post`；需要觀察完成或結果時使用 `InvokeAsync`。
- 已在 UI thread 時避免不必要的 dispatcher hop；需要顯性確認時使用 `CheckAccess` / `VerifyAccess`，control 或 library code 可依物件所屬 dispatcher 選擇 object dispatcher。
