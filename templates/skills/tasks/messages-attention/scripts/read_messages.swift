import Foundation
import SQLite3

let SQLITE_TRANSIENT = unsafeBitCast(-1, to: sqlite3_destructor_type.self)

struct MessageRow {
    let rowid: Int64
    let ts: String
    let chatID: Int64
    let isFromMe: Bool
    let handle: String?
    let text: String?
}

func parseArgs() -> (dbPath: String, since: String?, limit: Int) {
    var dbPath = NSHomeDirectory() + "/Library/Messages/chat.db"
    var since: String?
    var limit = 200

    var i = 1
    while i < CommandLine.arguments.count {
        let arg = CommandLine.arguments[i]
        switch arg {
        case "--db":
            i += 1
            if i < CommandLine.arguments.count { dbPath = CommandLine.arguments[i] }
        case "--since":
            i += 1
            if i < CommandLine.arguments.count { since = CommandLine.arguments[i] }
        case "--limit":
            i += 1
            if i < CommandLine.arguments.count, let parsed = Int(CommandLine.arguments[i]) { limit = parsed }
        default:
            break
        }
        i += 1
    }

    return (dbPath, since, limit)
}

func decodedText(rawText: UnsafePointer<UInt8>?, rawLen: Int32, attributedBody: Data?) -> String? {
    if let rawText {
        let text = String(cString: rawText)
        if !text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
            return text
        }
    }

    guard let attributedBody else { return nil }
    guard let object = NSUnarchiver.unarchiveObject(with: attributedBody) else { return nil }

    if let attributed = object as? NSAttributedString {
        let cleaned = attributed.string
            .replacingOccurrences(of: "\u{fffc}", with: "")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        return cleaned.isEmpty ? nil : cleaned
    }

    let fallback = String(describing: object)
        .replacingOccurrences(of: "\u{fffc}", with: "")
        .trimmingCharacters(in: .whitespacesAndNewlines)
    return fallback.isEmpty ? nil : fallback
}

func main() throws {
    let args = parseArgs()

    var db: OpaquePointer?
    guard sqlite3_open_v2(args.dbPath, &db, SQLITE_OPEN_READONLY, nil) == SQLITE_OK, let db else {
        throw NSError(domain: "read_messages", code: 1, userInfo: [NSLocalizedDescriptionKey: "Failed to open Messages DB at \(args.dbPath)"])
    }
    defer { sqlite3_close(db) }

    let baseSQL = """
    SELECT
      m.ROWID,
      datetime(m.date / 1000000000 + 978307200, 'unixepoch', 'localtime') AS ts,
      cmj.chat_id,
      m.is_from_me,
      h.id,
      m.text,
      m.attributedBody
    FROM message m
    JOIN chat_message_join cmj ON cmj.message_id = m.ROWID
    LEFT JOIN handle h ON h.ROWID = m.handle_id
    """

    let sql: String
    if args.since != nil {
        sql = baseSQL + " WHERE datetime(m.date / 1000000000 + 978307200, 'unixepoch', 'localtime') >= ? ORDER BY m.date DESC LIMIT ?"
    } else {
        sql = baseSQL + " ORDER BY m.date DESC LIMIT ?"
    }

    var stmt: OpaquePointer?
    guard sqlite3_prepare_v2(db, sql, -1, &stmt, nil) == SQLITE_OK, let stmt else {
        throw NSError(domain: "read_messages", code: 2, userInfo: [NSLocalizedDescriptionKey: "Failed to prepare query"])
    }
    defer { sqlite3_finalize(stmt) }

    var bindIndex: Int32 = 1
    if let since = args.since {
        sqlite3_bind_text(stmt, bindIndex, since, -1, SQLITE_TRANSIENT)
        bindIndex += 1
    }
    sqlite3_bind_int(stmt, bindIndex, Int32(args.limit))

    var output: [[String: Any]] = []

    while sqlite3_step(stmt) == SQLITE_ROW {
        let rowid = sqlite3_column_int64(stmt, 0)
        let ts = sqlite3_column_text(stmt, 1).map { String(cString: $0) } ?? ""
        let chatID = sqlite3_column_int64(stmt, 2)
        let isFromMe = sqlite3_column_int(stmt, 3) == 1
        let handle = sqlite3_column_text(stmt, 4).map { String(cString: $0) }
        let rawText = sqlite3_column_text(stmt, 5)

        var attributedData: Data?
        if let blob = sqlite3_column_blob(stmt, 6) {
            let len = Int(sqlite3_column_bytes(stmt, 6))
            attributedData = Data(bytes: blob, count: len)
        }

        let text = decodedText(rawText: rawText, rawLen: sqlite3_column_bytes(stmt, 5), attributedBody: attributedData)

        output.append([
            "rowid": rowid,
            "timestamp": ts,
            "chat_id": chatID,
            "is_from_me": isFromMe,
            "handle": handle as Any,
            "text": text as Any
        ])
    }

    let data = try JSONSerialization.data(withJSONObject: output, options: [.prettyPrinted, .sortedKeys])
    FileHandle.standardOutput.write(data)
    FileHandle.standardOutput.write("\n".data(using: .utf8)!)
}

do {
    try main()
} catch {
    fputs("read_messages.swift error: \(error)\n", stderr)
    exit(1)
}
