import Foundation
import SQLite3

let SQLITE_TRANSIENT = unsafeBitCast(-1, to: sqlite3_destructor_type.self)

struct Args {
    var dbPath = NSHomeDirectory() + "/Library/Messages/chat.db"
    var handleContains: String?
    var textContains: String?
    var filenameContains: String?
    var onDate: String?
    var since: String?
    var until: String?
    var incomingOnly = false
    var limit = 50
    var copyIndex: Int?
    var copyTo: String?
}

func parseArgs() -> Args {
    var args = Args()
    var i = 1

    while i < CommandLine.arguments.count {
        let arg = CommandLine.arguments[i]
        switch arg {
        case "--db":
            i += 1
            if i < CommandLine.arguments.count { args.dbPath = CommandLine.arguments[i] }
        case "--handle":
            i += 1
            if i < CommandLine.arguments.count { args.handleContains = CommandLine.arguments[i] }
        case "--text":
            i += 1
            if i < CommandLine.arguments.count { args.textContains = CommandLine.arguments[i] }
        case "--filename":
            i += 1
            if i < CommandLine.arguments.count { args.filenameContains = CommandLine.arguments[i] }
        case "--on-date":
            i += 1
            if i < CommandLine.arguments.count { args.onDate = CommandLine.arguments[i] }
        case "--since":
            i += 1
            if i < CommandLine.arguments.count { args.since = CommandLine.arguments[i] }
        case "--until":
            i += 1
            if i < CommandLine.arguments.count { args.until = CommandLine.arguments[i] }
        case "--incoming-only":
            args.incomingOnly = true
        case "--limit":
            i += 1
            if i < CommandLine.arguments.count, let parsed = Int(CommandLine.arguments[i]) {
                args.limit = parsed
            }
        case "--copy-index":
            i += 1
            if i < CommandLine.arguments.count, let parsed = Int(CommandLine.arguments[i]) {
                args.copyIndex = parsed
            }
        case "--copy-to":
            i += 1
            if i < CommandLine.arguments.count { args.copyTo = CommandLine.arguments[i] }
        default:
            break
        }
        i += 1
    }

    return args
}

func expandPath(_ path: String) -> String {
    (path as NSString).expandingTildeInPath
}

func buildQuery(_ args: Args) -> (String, [String]) {
    var conditions: [String] = []
    var bindings: [String] = []

    if let handleContains = args.handleContains, !handleContains.isEmpty {
        conditions.append("COALESCE(h.id, '') LIKE ?")
        bindings.append("%\(handleContains)%")
    }

    if let textContains = args.textContains, !textContains.isEmpty {
        conditions.append("COALESCE(m.text, '') LIKE ?")
        bindings.append("%\(textContains)%")
    }

    if let filenameContains = args.filenameContains, !filenameContains.isEmpty {
        conditions.append("COALESCE(a.filename, '') LIKE ?")
        bindings.append("%\(filenameContains)%")
    }

    if let onDate = args.onDate, !onDate.isEmpty {
        conditions.append("date(datetime(m.date / 1000000000 + 978307200, 'unixepoch', 'localtime')) = date(?)")
        bindings.append(onDate)
    }

    if let since = args.since, !since.isEmpty {
        conditions.append("datetime(m.date / 1000000000 + 978307200, 'unixepoch', 'localtime') >= datetime(?)")
        bindings.append(since)
    }

    if let until = args.until, !until.isEmpty {
        conditions.append("datetime(m.date / 1000000000 + 978307200, 'unixepoch', 'localtime') <= datetime(?)")
        bindings.append(until)
    }

    if args.incomingOnly {
        conditions.append("m.is_from_me = 0")
    }

    let whereClause = conditions.isEmpty ? "" : "WHERE " + conditions.joined(separator: " AND ")
    let sql = """
    SELECT
      datetime(m.date / 1000000000 + 978307200, 'unixepoch', 'localtime') AS local_time,
      COALESCE(h.id, '') AS handle,
      m.is_from_me,
      COALESCE(m.text, '') AS text,
      COALESCE(a.filename, '') AS filename,
      COALESCE(a.mime_type, '') AS mime_type,
      COALESCE(a.uti, '') AS uti,
      a.total_bytes
    FROM message m
    JOIN message_attachment_join maj ON maj.message_id = m.ROWID
    JOIN attachment a ON a.ROWID = maj.attachment_id
    LEFT JOIN handle h ON h.ROWID = m.handle_id
    \(whereClause)
    ORDER BY m.date DESC
    LIMIT ?
    """

    return (sql, bindings)
}

func bindText(_ stmt: OpaquePointer?, index: Int32, value: String) {
    sqlite3_bind_text(stmt, index, value, -1, SQLITE_TRANSIENT)
}

func runQuery(_ args: Args) throws -> [[String: Any]] {
    var db: OpaquePointer?
    let dbPath = expandPath(args.dbPath)
    guard sqlite3_open_v2(dbPath, &db, SQLITE_OPEN_READONLY, nil) == SQLITE_OK, let db else {
        throw NSError(domain: "find_message_attachments", code: 1, userInfo: [
            NSLocalizedDescriptionKey: "Failed to open Messages DB at \(dbPath)"
        ])
    }
    defer { sqlite3_close(db) }

    let (sql, bindings) = buildQuery(args)
    var stmt: OpaquePointer?
    guard sqlite3_prepare_v2(db, sql, -1, &stmt, nil) == SQLITE_OK, let stmt else {
        throw NSError(domain: "find_message_attachments", code: 2, userInfo: [
            NSLocalizedDescriptionKey: "Failed to prepare attachment query"
        ])
    }
    defer { sqlite3_finalize(stmt) }

    var bindIndex: Int32 = 1
    for binding in bindings {
        bindText(stmt, index: bindIndex, value: binding)
        bindIndex += 1
    }
    sqlite3_bind_int(stmt, bindIndex, Int32(args.limit))

    var rows: [[String: Any]] = []
    while sqlite3_step(stmt) == SQLITE_ROW {
        let localTime = sqlite3_column_text(stmt, 0).map { String(cString: $0) } ?? ""
        let handle = sqlite3_column_text(stmt, 1).map { String(cString: $0) } ?? ""
        let isFromMe = sqlite3_column_int(stmt, 2) == 1
        let text = sqlite3_column_text(stmt, 3).map { String(cString: $0) } ?? ""
        let filename = sqlite3_column_text(stmt, 4).map { String(cString: $0) } ?? ""
        let mimeType = sqlite3_column_text(stmt, 5).map { String(cString: $0) } ?? ""
        let uti = sqlite3_column_text(stmt, 6).map { String(cString: $0) } ?? ""
        let totalBytes = Int(sqlite3_column_int64(stmt, 7))

        rows.append([
            "local_time": localTime,
            "handle": handle,
            "is_from_me": isFromMe,
            "text": text,
            "filename": filename,
            "mime_type": mimeType,
            "uti": uti,
            "total_bytes": totalBytes
        ])
    }

    return rows
}

func copyAttachment(rows: [[String: Any]], args: Args) throws -> [String: Any]? {
    guard let copyIndex = args.copyIndex else { return nil }
    guard copyIndex >= 0, copyIndex < rows.count else {
        throw NSError(domain: "find_message_attachments", code: 3, userInfo: [
            NSLocalizedDescriptionKey: "copy index \(copyIndex) is out of range for \(rows.count) rows"
        ])
    }
    guard let copyTo = args.copyTo, !copyTo.isEmpty else {
        throw NSError(domain: "find_message_attachments", code: 4, userInfo: [
            NSLocalizedDescriptionKey: "--copy-to is required when using --copy-index"
        ])
    }

    let row = rows[copyIndex]
    guard let rawFilename = row["filename"] as? String, !rawFilename.isEmpty else {
        throw NSError(domain: "find_message_attachments", code: 5, userInfo: [
            NSLocalizedDescriptionKey: "selected row has no filename"
        ])
    }

    let sourcePath = expandPath(rawFilename)
    let destinationDir = URL(fileURLWithPath: expandPath(copyTo), isDirectory: true)
    try FileManager.default.createDirectory(at: destinationDir, withIntermediateDirectories: true)

    let destinationPath = destinationDir.appendingPathComponent(URL(fileURLWithPath: sourcePath).lastPathComponent)
    if FileManager.default.fileExists(atPath: destinationPath.path) {
        try FileManager.default.removeItem(at: destinationPath)
    }
    try FileManager.default.copyItem(at: URL(fileURLWithPath: sourcePath), to: destinationPath)

    return [
        "index": copyIndex,
        "source": sourcePath,
        "copied_to": destinationPath.path
    ]
}

func main() throws {
    let args = parseArgs()
    let rows = try runQuery(args)
    let copyResult = try copyAttachment(rows: rows, args: args)

    var payload: [String: Any] = [
        "count": rows.count,
        "results": rows
    ]
    if let copyResult {
        payload["copy_result"] = copyResult
    }

    let data = try JSONSerialization.data(withJSONObject: payload, options: [.prettyPrinted, .sortedKeys])
    FileHandle.standardOutput.write(data)
    FileHandle.standardOutput.write("\n".data(using: .utf8)!)
}

do {
    try main()
} catch {
    fputs("find_message_attachments.swift error: \(error)\n", stderr)
    exit(1)
}
