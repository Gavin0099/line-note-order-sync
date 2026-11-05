# C++ Build Boundary Rule Pack

- `AdditionalIncludeDirectories` 應只包含目前 project 自己的 tree，以及明確核准的 shared layer。
- 即使 build 能過，也不要把 peer project 的 private source directory 加進 include search path。
- cross-project private header access 應視為 boundary violation，不是便利性。
- 若多個 project 需要同一個 header，應抽到明確的 shared boundary component，並標清 ownership。
- 不要用「build 有過」之類理由合理化 hidden coupling。
