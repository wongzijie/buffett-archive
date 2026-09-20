# Validation record - 2026-09-20

The portable archive passed a full restore on macOS, including SHA-256 checks and SQLite integrity.
Six integration tests passed on macOS and Linux: document checksums, all vector norms,
counts, real search/context, source/year filters, bounded excerpts and exclusions.
All screened active transcripts were retrievable. All 47 excluded documents and all
of their stored chunk IDs remained inaccessible through the retrieval tools.
An actual MCP stdio initialize, tools/list, status, search and context round trip
passed on macOS and Linux with MCP 1.30.0.

All 16,649 exported vectors were compared byte for byte with the live source LanceDB
vectors and matched. The text/metadata/audit export scan found no private host paths,
private network endpoint, private keys or credential-shaped strings. This was a
bounded scan, not a formal security audit.

GitHub Actions repeats restore, integration tests and an actual MCP round trip on
Linux, macOS and Windows. Check the actual workflow results for the tested commit;
a workflow file alone is not proof that a platform passed.

The original live WeMM corpus was tested on RTX 5090 32 GB. The optional public
adapter preserves its pinned model revision and text encoding contract. Default CPU
tests do not test a fresh model download or establish support for every GPU.
None of these checks authenticates underlying recordings or sentence-level speakers.
