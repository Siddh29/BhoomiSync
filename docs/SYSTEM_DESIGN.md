# System design
See ../ARCHITECTURE.md for module boundaries. One FastAPI worker owns a serialized run; a lock rejects concurrent reset/run mutations. Readers receive the last complete snapshot while the next run executes. Failed runs expose an error and preserve the preceding result. Vite proxies /api locally. SQLite commits snapshots atomically. No network inputs.
