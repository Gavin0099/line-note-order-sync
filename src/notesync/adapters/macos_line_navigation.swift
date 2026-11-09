import AppKit
import ApplicationServices
import CoreGraphics
import Foundation

enum NavigationError: String, Error {
    case accessibilityDenied, loginRequired, mainUnavailable, chatUnavailable
    case notebookUnavailable, notebookNotFocused, notebookSearchFailed, unexpectedState
}

let lineBundleID = "jp.naver.line.mac"
let chatSearchLabels: Set<String> = ["搜尋聊天和訊息", "Search chats and messages"]
let mainSearchLabels = chatSearchLabels.union(["以姓名搜尋", "依名稱搜尋", "按名稱搜尋", "Search by name"])
let notebookLabels: Set<String> = ["記事本", "Notes"]
let notebookSearchLabels: Set<String> = ["搜尋", "Search"]
let loginLabels: Set<String> = ["登入", "使用行動條碼登入", "使用 QR Code 登入", "Log in", "Log in with QR code"]

func attribute<T>(_ element: AXUIElement, _ name: String) -> T? {
    var value: CFTypeRef?
    guard AXUIElementCopyAttributeValue(element, name as CFString, &value) == .success else {
        return nil
    }
    return value as? T
}

func elementAttribute(_ element: AXUIElement, _ name: String) -> AXUIElement? {
    let value: CFTypeRef? = attribute(element, name)
    guard let value, CFGetTypeID(value) == AXUIElementGetTypeID() else { return nil }
    return (value as! AXUIElement)
}

func labels(_ element: AXUIElement) -> Set<String> {
    let attributes = [kAXTitleAttribute, kAXDescriptionAttribute, kAXPlaceholderValueAttribute, kAXHelpAttribute]
    return Set(attributes.compactMap { name -> String? in
        let label: String? = attribute(element, name)
        return label?.replacingOccurrences(of: "&amp;", with: "&").trimmingCharacters(in: .whitespacesAndNewlines)
    })
}

func role(_ element: AXUIElement) -> String {
    attribute(element, kAXRoleAttribute) ?? ""
}

func nodes(_ root: AXUIElement) -> [AXUIElement] {
    var pending = [root]
    var result: [AXUIElement] = []
    while let element = pending.popLast() {
        result.append(element)
        let children: [AXUIElement] = attribute(element, kAXChildrenAttribute) ?? []
        guard result.count + pending.count + children.count <= 1200 else { return [] }
        pending.append(contentsOf: children.reversed())
    }
    return result
}

func frame(_ element: AXUIElement) -> CGRect? {
    let position: AXValue? = attribute(element, kAXPositionAttribute)
    let size: AXValue? = attribute(element, kAXSizeAttribute)
    var origin = CGPoint.zero
    var dimensions = CGSize.zero
    guard let position, let size, AXValueGetValue(position, .cgPoint, &origin),
          AXValueGetValue(size, .cgSize, &dimensions) else { return nil }
    return CGRect(origin: origin, size: dimensions)
}

func until<T>(_ seconds: TimeInterval, _ read: () -> T?) -> T? {
    let deadline = ProcessInfo.processInfo.systemUptime + seconds
    repeat {
        if let result = read() { return result }
        RunLoop.current.run(until: Date(timeIntervalSinceNow: 0.25))
    } while ProcessInfo.processInfo.systemUptime < deadline
    return nil
}

func unique<T>(_ values: [T]) -> T? {
    values.count == 1 ? values[0] : nil
}

func matchesChat(_ element: AXUIElement, _ chat: String) -> Bool {
    labels(element).contains { label in
        label == chat || label.replacingOccurrences(
            of: #"[,，]\s*[0-9][0-9,]*\s*(人|members)$"#, with: "", options: .regularExpression
        ) == chat
    }
}

func notebookButton(in window: AXUIElement, forChat chat: String) -> AXUIElement? {
    let controls = nodes(window)
    let headers = controls.filter { role($0) == kAXButtonRole && matchesChat($0, chat) }.compactMap(frame)
    return unique(controls.filter { button in
        guard role(button) == kAXButtonRole, !labels(button).isDisjoint(with: notebookLabels),
              let buttonFrame = frame(button), !buttonFrame.isEmpty else { return false }
        // LINE shows the selected chat's name immediately to the left of its toolbar.
        return headers.contains { header in
            !header.isEmpty && header.minX < buttonFrame.minX && abs(header.midY - buttonFrame.midY) <= 32
        }
    })
}

func windows(_ app: AXUIElement) -> [AXUIElement] {
    attribute(app, kAXWindowsAttribute) ?? []
}

func isFocused(_ window: AXUIElement, in app: AXUIElement, pid: pid_t) -> Bool {
    guard NSWorkspace.shared.frontmostApplication?.processIdentifier == pid,
          let focused = elementAttribute(app, kAXFocusedWindowAttribute) else { return false }
    return CFEqual(window, focused)
}

func searchField(in window: AXUIElement, labels allowed: Set<String>) -> AXUIElement? {
    unique(nodes(window).filter {
        role($0) == kAXTextFieldRole && !labels($0).isDisjoint(with: allowed)
    })
}

func openChatsTab(in app: AXUIElement) -> Bool {
    let viewLabels: Set<String> = ["顯示", "View"]
    let chatsLabels: Set<String> = ["聊天", "Chat", "Chats"]
    guard let bar = elementAttribute(app, kAXMenuBarAttribute),
          let view = unique(nodes(bar).filter({
              role($0) == kAXMenuBarItemRole && !labels($0).isDisjoint(with: viewLabels)
          })),
          let chats = unique(nodes(view).filter({
              role($0) == kAXMenuItemRole && !labels($0).isDisjoint(with: chatsLabels)
          })) else { return false }
    return AXUIElementPerformAction(chats, kAXPressAction as CFString) == .success
}

func matchesChatResult(_ element: AXUIElement, _ chat: String) -> Bool {
    // The Chats list exposes a cell title containing the room name at both ends.
    // The Friends tab has a similarly named button that opens the community lobby.
    guard role(element) == kAXCellRole else { return false }
    return labels(element).contains { label in
        label == chat || (label.hasPrefix(chat + ", ") && label.hasSuffix(", " + chat))
    }
}

func windowID(_ window: AXUIElement, pid: pid_t) -> Int? {
    guard let target = frame(window), !target.isEmpty else { return nil }
    let visible = CGWindowListCopyWindowInfo([.optionOnScreenOnly, .excludeDesktopElements], kCGNullWindowID)
        as? [[String: Any]] ?? []
    return unique(visible.compactMap { item in
        guard item[kCGWindowOwnerPID as String] as? pid_t == pid,
              item[kCGWindowLayer as String] as? Int == 0,
              let bounds = item[kCGWindowBounds as String] as? [String: Double],
              let x = bounds["X"], let y = bounds["Y"], let width = bounds["Width"], let height = bounds["Height"],
              abs(target.minX - x) <= 1, abs(target.minY - y) <= 1,
              abs(target.width - width) <= 1, abs(target.height - height) <= 1 else { return nil }
        return item[kCGWindowNumber as String] as? Int
    })
}

func isNotebook(_ window: AXUIElement) -> Bool {
    let title: String? = attribute(window, kAXTitleAttribute)
    if title.map(notebookLabels.contains) == true { return true }
    if title?.isEmpty != false, let size = frame(window),
       (280...620).contains(size.width), size.height >= 580,
       searchField(in: window, labels: notebookSearchLabels) != nil {
        return true
    }
    return nodes(window).contains { element in
        guard [kAXStaticTextRole, kAXHeadingRole].contains(role(element)) else { return false }
        let value: String? = attribute(element, kAXValueAttribute)
        return value.map(notebookLabels.contains) == true || !labels(element).isDisjoint(with: notebookLabels)
    }
}

func openNotebook(_ chat: String, reuse: Bool = false) throws -> Int {
    guard AXIsProcessTrusted() else { throw NavigationError.accessibilityDenied }
    guard let line = until(10, {
        unique(NSRunningApplication.runningApplications(withBundleIdentifier: lineBundleID))
    }) else { throw NavigationError.mainUnavailable }

    let pid = line.processIdentifier
    let app = AXUIElementCreateApplication(pid)
    _ = AXUIElementSetMessagingTimeout(app, 1)
    let main = until(18) {
        unique(windows(app).filter { searchField(in: $0, labels: mainSearchLabels) != nil })
    }
    guard let main else {
        let login = windows(app).flatMap(nodes).contains {
            if (attribute($0, kAXSubroleAttribute) as String?) == kAXSecureTextFieldSubrole { return true }
            if role($0) == kAXStaticTextRole, let value: String = attribute($0, kAXValueAttribute) {
                return value.contains("使用行動條碼登入") || value.contains("Log in with QR code")
            }
            return role($0) == kAXButtonRole && !labels($0).isDisjoint(with: loginLabels)
        }
        throw login ? NavigationError.loginRequired : NavigationError.mainUnavailable
    }
    _ = AXUIElementPerformAction(main, kAXRaiseAction as CFString)
    guard until(2, { isFocused(main, in: app, pid: pid) ? true : nil }) == true,
          windowID(main, pid: pid) != nil else { throw NavigationError.mainUnavailable }

    var button = notebookButton(in: main, forChat: chat)
    if button == nil {
        if searchField(in: main, labels: chatSearchLabels) == nil {
            guard isFocused(main, in: app, pid: pid), openChatsTab(in: app) else {
                throw NavigationError.chatUnavailable
            }
        }
        guard let field = until(4, { searchField(in: main, labels: chatSearchLabels) }),
              isFocused(main, in: app, pid: pid),
              AXUIElementSetAttributeValue(field, kAXValueAttribute as CFString, chat as CFString) == .success,
              (attribute(field, kAXValueAttribute) as String?) == chat,
              let target = until(6, {
                  unique(nodes(main).filter { matchesChatResult($0, chat) })
              }),
              isFocused(main, in: app, pid: pid),
              AXUIElementPerformAction(target, kAXPressAction as CFString) == .success else {
            throw NavigationError.chatUnavailable
        }
        button = until(6) { notebookButton(in: main, forChat: chat) }
    }
    let previousWindows = windows(app)
    guard let button, isFocused(main, in: app, pid: pid),
          AXUIElementPerformAction(button, kAXPressAction as CFString) == .success else {
        throw NavigationError.chatUnavailable
    }
    guard let id = until(8, {
        guard let focused = elementAttribute(app, kAXFocusedWindowAttribute),
              !CFEqual(focused, main),
              reuse || !previousWindows.contains(where: { CFEqual($0, focused) }) else { return nil as Int? }
        let title: String? = attribute(focused, kAXTitleAttribute)
        let compact = frame(focused).map { (280...620).contains($0.width) && $0.height >= 580 } == true
        // Some Qt frames omit the title and search control. In this mode the caller
        // verifies the notebook title in a window screenshot before sending input.
        guard isNotebook(focused) || (reuse && compact && title?.isEmpty != false) else { return nil }
        return windowID(focused, pid: pid)
    }) else { throw NavigationError.notebookUnavailable }
    return id
}

func pressKey(_ key: CGKeyCode, flags: CGEventFlags = []) -> Bool {
    guard let down = CGEvent(keyboardEventSource: nil, virtualKey: key, keyDown: true),
          let up = CGEvent(keyboardEventSource: nil, virtualKey: key, keyDown: false) else { return false }
    down.flags = flags
    up.flags = flags
    down.post(tap: .cghidEventTap)
    up.post(tap: .cghidEventTap)
    return true
}

func pasteSearchText(_ text: String) -> Bool {
    let board = NSPasteboard.general
    let previousCount = board.changeCount
    var previous: [NSPasteboardItem] = []
    var bytes = 0
    for item in board.pasteboardItems ?? [] {
        let copy = NSPasteboardItem()
        for type in item.types {
            guard let value = item.data(forType: type) else { return false }
            bytes += value.count
            guard bytes <= 16 * 1024 * 1024, copy.setData(value, forType: type) else { return false }
        }
        previous.append(copy)
    }
    guard board.changeCount == previousCount else { return false }
    board.clearContents()
    let written = board.setString(text, forType: .string)
    let ownCount = board.changeCount
    defer {
        if board.changeCount == ownCount {
            board.clearContents()
            if !previous.isEmpty { _ = board.writeObjects(previous) }
        }
    }
    guard written, pressKey(0, flags: .maskCommand) else { return false }
    RunLoop.current.run(until: Date(timeIntervalSinceNow: 0.08))
    guard pressKey(9, flags: .maskCommand) else { return false }
    RunLoop.current.run(until: Date(timeIntervalSinceNow: 0.35))
    return true
}

func notebookAction(_ args: [String]) throws -> [String: Any] {
    guard args.count >= 2, let id = Int(args[0]), AXIsProcessTrusted(),
          let line = unique(NSRunningApplication.runningApplications(withBundleIdentifier: lineBundleID))
    else { throw NavigationError.notebookUnavailable }
    let pid = line.processIdentifier
    let app = AXUIElementCreateApplication(pid)
    _ = AXUIElementSetMessagingTimeout(app, 1)
    guard let notebook = until(1, { unique(windows(app).filter { windowID($0, pid: pid) == id }) }),
          let bounds = frame(notebook), (280...620).contains(bounds.width), bounds.height >= 580
    else { throw NavigationError.notebookUnavailable }
    let verb = args[1]
    if verb == "resume", args.count == 2 {
        if !isFocused(notebook, in: app, pid: pid) {
            _ = line.activate(options: [])
            _ = AXUIElementPerformAction(notebook, kAXRaiseAction as CFString)
            guard until(2, { isFocused(notebook, in: app, pid: pid) ? true : nil }) == true
            else { throw NavigationError.notebookNotFocused }
        }
        return ["ok": true]
    }
    guard isFocused(notebook, in: app, pid: pid) else { throw NavigationError.notebookNotFocused }

    if verb == "close", args.count == 2 {
        guard let close = elementAttribute(notebook, kAXCloseButtonAttribute)
            ?? unique(nodes(notebook).filter { (attribute($0, kAXSubroleAttribute) as String?) == kAXCloseButtonSubrole }),
              let button = frame(close), !button.isEmpty,
              bounds.minX <= button.midX, button.midX <= bounds.minX + 30,
              bounds.minY <= button.midY, button.midY <= bounds.minY + 30 else {
            throw NavigationError.notebookUnavailable
        }
        let point = CGPoint(x: button.midX, y: button.midY)
        guard let down = CGEvent(mouseEventSource: nil, mouseType: .leftMouseDown, mouseCursorPosition: point, mouseButton: .left),
              let up = CGEvent(mouseEventSource: nil, mouseType: .leftMouseUp, mouseCursorPosition: point, mouseButton: .left)
        else { throw NavigationError.unexpectedState }
        _ = AXUIElementPerformAction(close, kAXPressAction as CFString)
        if until(0.7, { windowID(notebook, pid: pid) == nil ? true : nil }) != true {
            guard isFocused(notebook, in: app, pid: pid), windowID(notebook, pid: pid) == id
            else { throw NavigationError.notebookNotFocused }
            down.post(tap: .cghidEventTap)
            up.post(tap: .cghidEventTap)
        }
        guard until(2, { windowID(notebook, pid: pid) == nil ? true : nil }) == true
        else { throw NavigationError.notebookUnavailable }
        return ["ok": true]
    }
    if verb == "state", args.count == 2 {
        let field = searchField(in: notebook, labels: notebookSearchLabels)
        let fieldBounds = field.flatMap(frame)
        let query: String? = field.flatMap { attribute($0, kAXValueAttribute) }
        return ["width": bounds.width, "height": bounds.height, "query": query ?? "",
                "top": (fieldBounds.map { $0.maxY + 3 - bounds.minY } ?? 123) / bounds.height]
    }
    let searchInput = ["search-text", "submit-search"].contains(verb)
    guard args.count >= 4, let x = Double(args[2]), let y = Double(args[3]),
          (searchInput ? (0.05...0.42).contains(x) && (0.075...0.17).contains(y)
            : (0.02...0.98).contains(x) && (0.15...0.985).contains(y))
    else { throw NavigationError.unexpectedState }
    let point = CGPoint(x: bounds.minX + x * bounds.width, y: bounds.minY + y * bounds.height)
    let visible = CGWindowListCopyWindowInfo([.optionOnScreenOnly, .excludeDesktopElements], kCGNullWindowID)
        as? [[String: Any]] ?? []
    let hit = visible.first { item in
        guard item[kCGWindowLayer as String] as? Int == 0,
              let b = item[kCGWindowBounds as String] as? [String: Double],
              let minX = b["X"], let minY = b["Y"], let width = b["Width"], let height = b["Height"]
        else { return false }
        return CGRect(x: minX, y: minY, width: width, height: height).contains(point)
    }
    guard hit?[kCGWindowNumber as String] as? Int == id,
          isFocused(notebook, in: app, pid: pid) else { throw NavigationError.notebookNotFocused }
    if (verb == "click" && args.count == 4) || (verb == "submit-search" && args.count == 4)
        || (verb == "search-text" && args.count == 5),
       let down = CGEvent(mouseEventSource: nil, mouseType: .leftMouseDown, mouseCursorPosition: point, mouseButton: .left),
       let up = CGEvent(mouseEventSource: nil, mouseType: .leftMouseUp, mouseCursorPosition: point, mouseButton: .left) {
        down.post(tap: .cghidEventTap)
        up.post(tap: .cghidEventTap)
        if searchInput {
            RunLoop.current.run(until: Date(timeIntervalSinceNow: 0.12))
            guard isFocused(notebook, in: app, pid: pid) else { throw NavigationError.notebookNotFocused }
            if verb == "search-text" {
                let text = args[4]
                guard !text.isEmpty, text.count <= 200,
                      text.unicodeScalars.allSatisfy({ !CharacterSet.controlCharacters.contains($0) }),
                      pasteSearchText(text)
                else { throw NavigationError.notebookSearchFailed }
            } else {
                guard pressKey(36) else { throw NavigationError.notebookSearchFailed }
            }
        }
    } else if verb == "scroll", args.count == 5, let delta = Int32(args[4]), (-950...950).contains(delta),
              let event = CGEvent(scrollWheelEvent2Source: nil, units: .pixel, wheelCount: 1,
                                  wheel1: delta, wheel2: 0, wheel3: 0) {
        event.location = point
        event.post(tap: .cghidEventTap)
    } else {
        throw NavigationError.unexpectedState
    }
    return ["ok": true]
}

do {
    let args = Array(CommandLine.arguments.dropFirst())
    let result: [String: Any]
    if args.first == "--notebook-action" {
        result = try notebookAction(Array(args.dropFirst()))
    } else {
        guard args.count == 1 || (args.count == 2 && args[1] == "--reuse") else {
            throw NavigationError.unexpectedState
        }
        result = ["window": try openNotebook(args[0], reuse: args.count == 2)]
    }
    FileHandle.standardOutput.write(try JSONSerialization.data(withJSONObject: result))
} catch {
    let code = (error as? NavigationError ?? .unexpectedState).rawValue
    FileHandle.standardOutput.write(Data("{\"error\":\"\(code)\"}".utf8))
    exit(1)
}
