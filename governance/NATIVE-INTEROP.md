---
audience: agent-on-demand
authority: reference
can_override: false
overridden_by: AGENT.md
default_load: on-demand
---

# NATIVE-INTEROP.md
**Native Interop 協定 - v3.0**

> **Version**: 3.0 | **Priority**: 7（實體安全）
>
> P/Invoke 與 ABI guardrail 的可執行規格。
> 違反任一規則時，**立即 STOP，並依 `HUMAN-OVERSIGHT.md` escalate**。

---

## 0. Scope

當 task 涉及以下任一項時，必須載入並執行本文件：
- P/Invoke
- native library call（`.dll` / `.so` / `.framework`）
- ABI / binary marshalling
- C# 與 unmanaged 語言之間的 data / resource transfer

如果連適用性都不清楚，**STOP 並詢問**。

---

## 1. Data Integrity

### 1.1 Layout Safety（Mandatory）

所有跨語言 `struct` **必須**：
- 使用 `[StructLayout(LayoutKind.Sequential)]`
- 明確指定 `Pack`

依賴 default alignment 或 compiler inference，屬於禁止的 native call 前提。

### 1.2 String Encoding（Mandatory）

預設使用 UTF-8。C# 端使用 `[MarshalAs(UnmanagedType.LPUTF8Str)]`。
Native 端必須明確定義：
- string 是否被複製
- pointer 是否會被保留

如果 string lifetime 不明，**STOP**。

### 1.3 Memory Ownership（Highest-Risk Red Line）

所有跨邊界 memory **都必須**明確定義：
- allocator 是誰
- deallocator 是誰
- ownership 是否轉移

禁止：
- double free
- implicit ownership

要求：
- native allocation 必須提供對應的 `FreeXXX()` API
- C# 端必須用 `try/finally` 或 `SafeHandle`

如果答不出「誰負責釋放」，就應**拒絕通過**。

---

## 2. Resource Management

### 2.1 SafeHandle（Mandatory）

native pointer **不得**以 raw `IntPtr` 穿出 Adapter layer；應包成 `SafeHandle`。

若 `IntPtr` 出現在 Service / Domain，屬於 architecture violation。

### 2.2 IDisposable（Mandatory）

持有 native resource 的 adapter **必須**實作 `IDisposable` 與 Finalizer。
`Dispose` 必須是 idempotent，且可安全面對重複呼叫。

---

## 3. Platform 與 ABI

### 3.1 Calling Convention（Mandatory）

在 Windows 上，`CallingConvention` **必須**明確指定。
不允許依賴 default 或 inferred convention。

### 3.2 Platform Probing（Mandatory）

在載入任何 native library 前，**必須**先做 `IsPlatformSupported()` 檢查：
- OS
- architecture（x64 / arm64）
- ABI compatibility

未 probing 就直接 load，應**拒絕**。

### 3.3 Library Loading（Cross-Platform Red Line）

禁止：
- hard-coded library name
- absolute path load

要求：
- 優先使用 `LibraryImport`
- 使用 `NativeLibrary.SetDllImportResolver`
- 集中到 `Infrastructure.NativeLibraryLoader`

若無法安全載入，應拋 `PlatformNotSupportedException`。

---

## 4. Error Boundary

### 4.1 Error Severity Classification（Mandatory）

所有 native error **必須**被歸類成以下兩種之一：

| Category | Examples | Handling |
|---|---|---|
| **Logic Error**（可恢復） | File not found、invalid parameter、device disconnected、timeout | 轉成 `Result<T, E>`，可往 Domain 傳遞 |
| **Panic / Crash**（不可恢復） | Access Violation、memory corruption、stack overflow、segfault | **在 Infrastructure layer FailFast**，不得進入 Domain |

對 Panic / Crash 的規則：
- 必須在最外層 Infrastructure boundary 處理
- 終止前必須先記錄 diagnostic info
- 必須觸發 `Environment.FailFast()`，不得包成 `Result<T, E>`
- 若不確定是否可恢復，預設視為 Panic

### 4.2 Native Error Isolation（Mandatory）

native layer **不得**把 exception 直接丟過邊界；應回傳 `int / enum / struct` status code。
C++ / ObjC 應以 `try/catch` 轉成 return code。

#### Crash Handling（極端情況）

```csharp
public class CriticalNativeCrashException : Exception
{
    public CriticalNativeCrashException(string message, int errorCode, string platform)
        : base($"{message} (Code: {errorCode}, Platform: {platform})") { }
}
```

這種 exception 只用於 logging 與 diagnostics，不得被 catch 後靜默繼續。

### 4.3 Adapter Error Translation（Mandatory）

Logic error 應轉成 `Result<T, E>` 或 `ARCHITECTURE.md` 定義的等價形式。

禁止：
- raw numeric error code 進入 Domain
- 將 panic-level error 包成 `Result`

---

## 5. Testing

本文件與 `TESTING.md` 搭配使用。所有 native interop **必須**至少有：
- characterization / contract test 來鎖住行為
- 驗證 memory layout correctness、resource release、error translation
- **error classification test**：確認 panic-level error 會觸發 FailFast，而不是變成 Result
- L2 情況下，至少在兩個平台上做 integration test

---

## 6. ADR Triggers

以下決策一旦出現，就**必須建立 ADR**：
- memory ownership strategy
- cross-platform loading difference
- ABI / calling convention
- `LibraryImport` vs `DllImport`

ADR 格式與流程依 `ARCHITECTURE.md` 第 6 節。

---

## Final Principle

> **Native interop 是 trust boundary。只要有不清楚的地方，安全上就應視為不成立。**
>
> **如果無法說清楚資料如何跨邊界、誰釋放資源、失敗時會發生什麼，就必須 STOP。**
