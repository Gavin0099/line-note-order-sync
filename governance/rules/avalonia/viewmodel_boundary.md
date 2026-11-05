# Avalonia ViewModel Boundary

- ViewModel 的職責是協調 presentation state；它不應變成無邊界的 I/O 或 platform logic integration layer。
- native call、filesystem access、與 process launch 行為應放在 service 或 adapter 後面。
- headless testability 是 governance concern：UI behavior 應能在不靠完整人工互動的情況下被觀測。
