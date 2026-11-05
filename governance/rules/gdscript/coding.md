# GDScript Rule Pack

- 明確宣告 `LANG = GDScript`；跨語言工作使用逗號分隔，例如 `GDScript, Python`。
- 保持 Domain 與 Godot 場景、Node、UI、資源載入及 filesystem 的責任邊界明確；既有專案架構由專案合約決定。
- 原生檢查由 consuming repo 的 validator 綁定固定 Godot 版本與實際專案；缺少引擎、解析失敗或場景載入失敗不能記為通過。
- 分別記錄語法／匯入、啟動與玩法測試的證據；框架 Python 測試及規則載入成功不代表 GDScript 遊戲已通過驗收。

本 pack 提供語言治理上下文，不執行 Godot、不新增 runtime gate，也不核准領域風險分級。
