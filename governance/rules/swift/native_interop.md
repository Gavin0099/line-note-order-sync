# Swift Native Interop

- 當 Objective-C bridging 或 native platform API 會影響 domain logic 時，它們必須被放在明確邊界後面。
- `unsafe pointer` 或 unmanaged resource handling 必須說清 ownership 與 cleanup rule。
- platform capability check 不應靜默滲入較高層的 business rule。
