# Versioned database snapshot

The compressed SQLite archive is split into numbered parts. Run `python setup_archive.py` from the repository root; do not open or extract a part on its own. SHA-256 hashes in manifest.json verify every part and the restored database. No Git LFS or account is required to download this public snapshot.
