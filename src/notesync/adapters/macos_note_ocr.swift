import AppKit
import CoreGraphics
import Foundation
import ImageIO
import Vision

enum CaptureError: Error {
    case invalidImage, unsupportedLanguage, invalidArguments
}

func lineWindows() -> [[String: Int]] {
    let pids = Set(NSRunningApplication.runningApplications(
        withBundleIdentifier: "jp.naver.line.mac"
    ).map(\.processIdentifier))
    let windows = CGWindowListCopyWindowInfo(
        [.optionOnScreenOnly, .excludeDesktopElements], kCGNullWindowID
    ) as? [[String: Any]] ?? []
    return windows.compactMap { window in
        guard let pid = window[kCGWindowOwnerPID as String] as? Int32, pids.contains(pid),
              window[kCGWindowLayer as String] as? Int == 0,
              let id = window[kCGWindowNumber as String] as? Int,
              let bounds = window[kCGWindowBounds as String] as? [String: Double],
              let width = bounds["Width"], let height = bounds["Height"],
              width >= 250, height >= 250 else { return nil }
        return ["id": id, "width": Int(width), "height": Int(height)]
    }
}

func recognize(_ url: URL, headerOnly: Bool = false) throws -> [String: Any] {
    guard let source = CGImageSourceCreateWithURL(url as CFURL, nil),
          let properties = CGImageSourceCopyPropertiesAtIndex(source, 0, nil) as? [CFString: Any],
          let width = properties[kCGImagePropertyPixelWidth] as? Int,
          let height = properties[kCGImagePropertyPixelHeight] as? Int,
          width > 0, height > 0, width <= 6000, height <= 6000,
          let original = CGImageSourceCreateImageAtIndex(source, 0, nil) else {
        throw CaptureError.invalidImage
    }
    let image: CGImage
    if headerOnly {
        guard let crop = original.cropping(to: CGRect(x: Double(width) * 0.34, y: Double(height) * 0.032,
                                                      width: Double(width) * 0.32, height: Double(height) * 0.06).integral)
        else { throw CaptureError.invalidImage }
        image = crop
    } else {
        image = original
    }
    let scale = image.width < 900 ? min(3, 1500 / image.width) : 1
    var input = image
    if scale > 1, let context = CGContext(
        data: nil, width: image.width * scale, height: image.height * scale,
        bitsPerComponent: 8, bytesPerRow: 0, space: CGColorSpaceCreateDeviceRGB(),
        bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue
    ) {
        context.interpolationQuality = .high
        context.draw(image, in: CGRect(x: 0, y: 0, width: context.width, height: context.height))
        input = context.makeImage() ?? image
    }

    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    let languages = try request.supportedRecognitionLanguages()
    guard languages.contains("zh-Hant") else { throw CaptureError.unsupportedLanguage }
    request.recognitionLanguages = ["zh-Hant", "en-US"].filter(languages.contains)
    request.usesLanguageCorrection = false
    try VNImageRequestHandler(cgImage: input, options: [:]).perform([request])
    let lines: [[String: Any]] = (request.results ?? []).compactMap { observation in
        let candidates = observation.topCandidates(3)
        guard let text = candidates.first else { return nil }
        let box = observation.boundingBox
        return ["text": text.string, "x": box.minX, "y": 1 - box.maxY, "w": box.width,
                "h": box.height, "confidence": text.confidence,
                "alternatives": candidates.dropFirst().map(\.string)]
    }
    return ["width": image.width, "height": image.height, "lines": lines]
}

// The comment icon has three separated dots between its left and right edges.
// Sample at point scale so this also works with Retina window captures.
func hasCommentBubble(_ url: URL, x: Double, y: Double, scale: Double) -> Bool {
    guard (0.9...3.0).contains(scale), (0...1).contains(x), (0...1).contains(y),
          let source = CGImageSourceCreateWithURL(url as CFURL, nil),
          let image = CGImageSourceCreateImageAtIndex(source, 0, nil) else { return false }
    let crop = CGRect(x: x * Double(image.width) - 11 * scale,
                      y: y * Double(image.height) - 8 * scale,
                      width: 22 * scale, height: 16 * scale).integral
    guard CGRect(x: 0, y: 0, width: image.width, height: image.height).contains(crop),
          let icon = image.cropping(to: crop),
          let gray = CGContext(data: nil, width: 22, height: 16, bitsPerComponent: 8,
                               bytesPerRow: 22, space: CGColorSpaceCreateDeviceGray(),
                               bitmapInfo: CGImageAlphaInfo.none.rawValue),
          let data = gray.data else { return false }
    gray.draw(icon, in: CGRect(x: 0, y: 0, width: 22, height: 16))
    let pixels = data.bindMemory(to: UInt8.self, capacity: 352)
    for row in 4...11 {
        let start = row * 22
        let background = Int(pixels[start])
        var runs: [Int] = []
        var marked = false
        for col in 1..<21 {
            let foreground = abs(Int(pixels[start + col]) - background) >= 56
            if foreground && !marked { runs.append(col) }
            marked = foreground
        }
        if runs.count == 5, (12...19).contains(runs[4] - runs[0]), (8...13).contains((runs[0] + runs[4]) / 2),
           (2...4).contains(runs[2] - runs[1]), (2...4).contains(runs[3] - runs[2]) {
            return true
        }
    }
    return false
}

func viewportPixels(_ path: String, columns: Int) throws -> (Int, Int, [UInt8]) {
    let url = URL(fileURLWithPath: path)
    guard let source = CGImageSourceCreateWithURL(url as CFURL, nil),
          let image = CGImageSourceCreateImageAtIndex(source, 0, nil),
          (250...2000).contains(image.width), (480...3200).contains(image.height),
          let cropped = image.cropping(to: CGRect(x: 12, y: 0, width: image.width - 36, height: image.height)),
          let context = CGContext(data: nil, width: columns, height: image.height, bitsPerComponent: 8,
                                  bytesPerRow: columns, space: CGColorSpaceCreateDeviceGray(),
                                  bitmapInfo: CGImageAlphaInfo.none.rawValue),
          let pixels = context.data else { throw CaptureError.invalidImage }
    context.interpolationQuality = .medium
    context.draw(cropped, in: CGRect(x: 0, y: 0, width: columns, height: image.height))
    let bytes = pixels.bindMemory(to: UInt8.self, capacity: columns * image.height)
    return (image.width, image.height, Array(UnsafeBufferPointer(start: bytes, count: columns * image.height)))
}

// Measure actual movement of overlapping content. Mouse wheel deltas are not
// viewport offsets, and text labels alone cannot establish frame continuity.
func viewportShift(_ previous: String, _ current: String, expected: Int?) throws -> Int? {
    let columns = 20
    let (width, height, first) = try viewportPixels(previous, columns: columns)
    let (newWidth, newHeight, second) = try viewportPixels(current, columns: columns)
    guard width == newWidth, height == newHeight else { return nil }
    let top = Int(Double(height) * 0.18)
    let bottom = height - 10
    let limit = Int(Double(height) * 0.68)
    let firstRows = (0..<height).map { y -> Bool in
        let line = first[(y * columns)..<((y + 1) * columns)]
        return Int(line.max() ?? 0) - Int(line.min() ?? 0) >= 16
    }
    let secondRows = (0..<height).map { y -> Bool in
        let line = second[(y * columns)..<((y + 1) * columns)]
        return Int(line.max() ?? 0) - Int(line.min() ?? 0) >= 16
    }
    var candidates: [(Int, Double)] = []
    for shift in -limit...limit {
        if let expected, shift != 0, (shift.signum() != expected.signum()
            || abs(shift) > abs(expected) + max(24, abs(expected) / 5)) { continue }
        let start = max(top, top - shift)
        let end = min(bottom, bottom - shift)
        var error = 0
        var rows = 0
        for y in stride(from: start, to: end, by: 3) where firstRows[y + shift] || secondRows[y] {
            for x in 0..<columns {
                error += abs(Int(first[(y + shift) * columns + x]) - Int(second[y * columns + x]))
            }
            rows += 1
        }
        if rows >= 23 { candidates.append((shift, Double(error) / Double(rows * columns))) }
    }
    guard let best = candidates.min(by: { $0.1 < $1.1 }), best.1 <= 6,
          !candidates.contains(where: { abs($0.0 - best.0) > 4 && $0.1 < best.1 + 1 })
    else { return first == second ? 0 : nil }
    return best.0
}

do {
    let args = Array(CommandLine.arguments.dropFirst())
    if args == ["windows"] {
        FileHandle.standardOutput.write(try JSONSerialization.data(withJSONObject: ["windows": lineWindows()]))
    } else if args.count == 3, ["recognize", "header"].contains(args[0]) {
        let result = try recognize(URL(fileURLWithPath: args[1]), headerOnly: args[0] == "header")
        try JSONSerialization.data(withJSONObject: result).write(to: URL(fileURLWithPath: args[2]))
    } else if args.count == 5, args[0] == "bubble",
              let x = Double(args[2]), let y = Double(args[3]), let scale = Double(args[4]) {
        let visible = hasCommentBubble(URL(fileURLWithPath: args[1]), x: x, y: y, scale: scale)
        FileHandle.standardOutput.write(try JSONSerialization.data(withJSONObject: ["visible": visible]))
    } else if (3...4).contains(args.count), args[0] == "motion" {
        let shift = try viewportShift(args[1], args[2], expected: args.count == 4 ? Int(args[3]) : nil)
        FileHandle.standardOutput.write(try JSONSerialization.data(withJSONObject: ["shift": shift as Any? ?? NSNull()]))
    } else {
        throw CaptureError.invalidArguments
    }
} catch {
    FileHandle.standardError.write(Data("\(error)\n".utf8))
    exit(2)
}
