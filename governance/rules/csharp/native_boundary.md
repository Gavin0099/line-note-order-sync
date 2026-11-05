# C# Native Boundary

- native interop 必須留在明確的 adapter 或 boundary interface 後面。
- `DllImport` 與 native handle management 不得滲入 domain logic。
- resource ownership、dispose、與 error translation 必須明確且可 review。
