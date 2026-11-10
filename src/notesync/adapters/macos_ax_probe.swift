import AppKit
import ApplicationServices
import Foundation

enum ProbeError: String, Error {
    case lineNotRunning, accessibilityDenied, noWindows, invalidWindow, elementUnavailable, readFailed
}

func attribute<T>(_ element: AXUIElement, _ name: String) throws -> T? {
    var value: CFTypeRef?
    switch AXUIElementCopyAttributeValue(element, name as CFString, &value) {
    case .success:
        return value as? T
    case .attributeUnsupported, .noValue, .notImplemented:
        return nil
    case .apiDisabled:
        throw ProbeError.accessibilityDenied
    case .invalidUIElement:
        throw ProbeError.elementUnavailable
    default:
        throw ProbeError.readFailed
    }
}

func textElements(in window: AXUIElement, processID: pid_t) throws -> ([[String: Any]], Bool) {
    let editableRoles = ["AXTextField", "AXTextArea", "AXComboBox", "AXSecureTextField"]
    let valueRoles = ["AXStaticText", "AXHeading", "AXLink"]
    var pending = [(element: window, depth: 0)]
    var rows: [[String: Any]] = []
    var visited = 0
    var textSize = 0
    var partial = false

    while let item = pending.popLast() {
        if visited == 1500 { return (rows, true) }
        visited += 1
        do {
            var owner: pid_t = 0
            let pidStatus = AXUIElementGetPid(item.element, &owner)
            if pidStatus == .invalidUIElement { throw ProbeError.elementUnavailable }
            guard pidStatus == .success else { throw ProbeError.readFailed }
            guard owner == processID else { continue }
            let role: String = try attribute(item.element, kAXRoleAttribute) ?? ""
            let subrole: String = try attribute(item.element, kAXSubroleAttribute) ?? ""
            guard !editableRoles.contains(role), subrole != "AXSecureTextField" else { continue }

            let children: [AXUIElement] = try attribute(item.element, kAXChildrenAttribute) ?? []
            let remaining = 1500 - visited - pending.count
            if children.count > remaining { partial = true }
            pending.append(contentsOf: children.prefix(remaining).reversed().map { ($0, item.depth + 1) })
            guard item.depth > 0 else { continue }

            var row: [String: Any] = ["depth": item.depth, "role": role]
            var rowSize = 0
            let labels = [("title", kAXTitleAttribute), ("description", kAXDescriptionAttribute)]
            let fields = valueRoles.contains(role) ? labels + [("text", kAXValueAttribute)] : labels
            for (key, name) in fields {
                guard let text: String = try attribute(item.element, name),
                      !text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { continue }
                let size = text.utf8.count
                if size > 32768 {
                    partial = true
                    continue
                }
                row[key] = text
                rowSize += size
            }
            if rowSize == 0 { continue }
            textSize += rowSize
            if textSize > 300000 { return (rows, true) }
            rows.append(row)
        } catch ProbeError.elementUnavailable where item.depth > 0 {
            // LINE can replace nodes while its list is virtualized.
            partial = true
        }
    }
    return (rows, partial)
}

func probe(_ arguments: [String]) throws -> [String: Any] {
    guard let line = NSRunningApplication.runningApplications(withBundleIdentifier: "jp.naver.line.mac").first
    else { throw ProbeError.lineNotRunning }
    guard AXIsProcessTrusted() else { throw ProbeError.accessibilityDenied }
    let processID = line.processIdentifier
    let application = AXUIElementCreateApplication(processID)
    guard AXUIElementSetMessagingTimeout(application, 2) == .success else { throw ProbeError.readFailed }
    let windows: [AXUIElement] = try attribute(application, kAXWindowsAttribute) ?? []
    if arguments == ["list"] {
        return ["windows": try windows.enumerated().map { index, window in
            let title: String = try attribute(window, kAXTitleAttribute) ?? ""
            return ["window": index + 1, "title": title]
        }]
    }
    guard !windows.isEmpty else { throw ProbeError.noWindows }
    guard arguments.count == 1, let number = Int(arguments[0]),
          number > 0, number <= windows.count else { throw ProbeError.invalidWindow }
    let window = windows[number - 1]
    let title: String = try attribute(window, kAXTitleAttribute) ?? ""
    let (elements, partial) = try textElements(in: window, processID: processID)
    return ["window": number, "window_title": title, "elements": elements, "incomplete_read": partial]
}

do {
    let output = try probe(Array(CommandLine.arguments.dropFirst()))
    let json = try JSONSerialization.data(withJSONObject: output)
    FileHandle.standardOutput.write(json)
} catch {
    let code = (error as? ProbeError ?? .readFailed).rawValue
    FileHandle.standardOutput.write(Data("{\"error\":\"\(code)\"}".utf8))
    exit(1)
}
