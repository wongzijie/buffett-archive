# Portable logical backup

The ordered gzip parts restore one standard SQLite file. No LanceDB runtime is needed.

- documents: ID, relative source filename, complete Markdown, exported text SHA-256, active flag.
- chunks: stable IDs, cleaned text, original embedding input, ordering, character offsets, metadata JSON, active flag.
- vectors: chunk ID plus 1024 little-endian float32 values (4096 bytes).
- search: FTS5 index containing active chunks only.
- info: JSON-encoded version, model contract, counts and screening metadata.

All 459 stored documents and 16,649 chunks/vectors are backed up. 47 inactive documents
are retained for historical recovery. Direct SQL can read them; active is a retrieval
rule, not encryption. The CLI and MCP enforce the scope.

This is a logical backup, not a server disk image. Personal paths are removed and
machine configuration, service logs, credentials, audio/video and model weights are
not included. Raw intake materials never imported into the database are not implied
by the 459-document count; their review ledger is provided.

Runtime verifies the published database checksum. For a new dataset release, intentionally
rebuild and validate the manifest; never disable validation to force an installation.
