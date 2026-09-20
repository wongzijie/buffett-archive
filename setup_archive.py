"""Offline, dependency-free restore of the versioned corpus. Python 3.10+."""
from pathlib import Path
from contextlib import closing
import gzip,hashlib,json,os,sqlite3,sys,tempfile
ROOT=Path(__file__).resolve().parent

def sha256(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()

def main():
 if sys.version_info<(3,10):raise SystemExit('Python 3.10 or newer is required.')
 manifest=json.loads((ROOT/'data/manifest.json').read_text())
 dest=ROOT/'runtime/archive.sqlite';dest.parent.mkdir(exist_ok=True)
 if dest.exists():
  if sha256(dest)==manifest['database_sha256']:
   print('Already installed and checksum verified:',dest);return
  raise SystemExit('Existing database differs. Move runtime/archive.sqlite aside before restoring; nothing overwritten.')
 parts=manifest['archive_parts']
 for name in ['content_audit.json','retrieval_scope.json']+parts:
  path=ROOT/'data'/name
  if sha256(path)!=manifest['files'][name]['sha256']:raise SystemExit('Checksum failed: '+name)
 fd,tmp=tempfile.mkstemp(prefix='restore-',suffix='.sqlite',dir=dest.parent);os.close(fd)
 try:
  with tempfile.TemporaryFile() as compressed:
   h=hashlib.sha256()
   for name in parts:
    with (ROOT/'data'/name).open('rb') as src:
     for block in iter(lambda:src.read(1024*1024),b''):compressed.write(block);h.update(block)
   if h.hexdigest()!=manifest['archive_sha256']:raise ValueError('Combined archive checksum mismatch')
   compressed.seek(0)
   total=0
   with gzip.GzipFile(fileobj=compressed,mode='rb') as src,open(tmp,'wb') as dst:
    for block in iter(lambda:src.read(1024*1024),b''):
     total+=len(block)
     if total>manifest['database_bytes']:raise ValueError('Unexpected decompressed size')
     dst.write(block)
  if total!=manifest['database_bytes'] or sha256(tmp)!=manifest['database_sha256']:raise ValueError('Database checksum mismatch')
  with closing(sqlite3.connect(tmp)) as db:
   if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('SQLite integrity check failed')
   for table,key,active in [('documents','stored_documents',False),('chunks','stored_chunks',False),('documents','active_documents',True),('chunks','active_chunks',True)]:
    count=db.execute('SELECT count(*) FROM '+table+(' WHERE active=1' if active else '')).fetchone()[0]
    if count!=manifest[key]:raise ValueError('Count mismatch: '+key)
   if db.execute('SELECT count(*) FROM vectors').fetchone()[0]!=manifest['stored_chunks']:raise ValueError('Missing vectors')
  os.replace(tmp,dest)
 finally:
  if Path(tmp).exists():Path(tmp).unlink()
 print('Ready: 412 searchable documents, 16,065 chunks; 459 documents backed up.')
 print('Try: python archive.py search "insurance float"')
 print('MCP (optional): python -m pip install -r requirements-mcp.txt; python archive.py mcp')
if __name__=='__main__':main()
