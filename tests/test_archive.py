import json,sqlite3,sys,unittest,hashlib,math,struct
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from archive import Archive
from setup_archive import ROOT
class ArchiveTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.archive=Archive()
 def test_counts_and_vector_integrity(self):
  with self.archive.connect() as db:
   self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0],'ok')
   self.assertEqual(db.execute('SELECT count(*) FROM documents').fetchone()[0],459)
   self.assertEqual(db.execute('SELECT count(*) FROM documents WHERE active=1').fetchone()[0],412)
   self.assertEqual(db.execute('SELECT count(*) FROM chunks WHERE active=1').fetchone()[0],16065)
   self.assertEqual(db.execute('SELECT count(*) FROM vectors').fetchone()[0],16649)
   for (blob,) in db.execute('SELECT vector FROM vectors'):
    vec=struct.unpack('<1024f',blob);self.assertTrue(all(math.isfinite(x) for x in vec));self.assertAlmostEqual(sum(x*x for x in vec),1,places=5)
 def test_all_source_checksums(self):
  with self.archive.connect() as db:
   for r in db.execute('SELECT markdown,source_sha256 FROM documents'):
    self.assertEqual(hashlib.sha256(r[0].encode()).hexdigest(),r[1])
 def test_all_exclusions_cannot_be_bypassed(self):
  with self.archive.connect() as db:
   docs=list(db.execute('SELECT doc_id FROM documents WHERE active=0'))
   self.assertEqual(len(docs),47)
   for (did,) in docs:
    result=self.archive.search('Warren Buffett',filters={'doc_id':did,'include_unverified':True})
    self.assertEqual(result['results'],[])
    for (cid,) in db.execute('SELECT chunk_id FROM chunks WHERE doc_id=?',(did,)):
     with self.assertRaises(ValueError):self.archive.context(cid)
 def test_real_search_budget_and_context(self):
  r=self.archive.search('insurance float',top_k=3,max_chars=1000)
  self.assertTrue(r['results']);self.assertLessEqual(r['context_chars'],1000)
  h=r['results'][0];full=self.archive.context(h['chunk_id'])['result']
  self.assertTrue(full['text'].startswith(h['text']));self.assertIn('authenticity',h['metadata']);self.assertIn('source_url',h['metadata'])
 def test_every_screened_active_document_is_searchable(self):
  with self.archive.connect() as db:
   rows=list(db.execute('SELECT * FROM chunks WHERE active=1 AND chunk_index=0'))
  tested=0
  for row in rows:
   m=json.loads(row['metadata_json'])
   if m.get('content_review',{}).get('decision')!='retain_candidate':continue
   r=self.archive.search(row['text'][:250],top_k=1,filters={'doc_id':row['doc_id']})
   self.assertTrue(r['results'],row['doc_id']);self.assertEqual(r['results'][0]['metadata']['authenticity'],m['authenticity']);tested+=1
  self.assertGreaterEqual(tested,316)
 def test_filters_and_validation(self):
  r=self.archive.search('insurance float',filters={'official_sources_only':True})
  self.assertTrue(r['results']);self.assertTrue(all(h['metadata']['authenticity']=='official_source_verified' for h in r['results']))
  r=self.archive.search('insurance float',filters={'year_min':2008,'year_max':2009})
  self.assertTrue(r['results']);self.assertTrue(all(2008<=h['metadata']['event_year']<=2009 for h in r['results']))
  self.assertEqual(self.archive.search('float',filters={'doc_id':"x' OR 1=1 --"})['results'],[])
  for kwargs in ({'top_k':True},{'mode':'semantic'},{'max_chars':0},{'filters':{'year_min':True}},{'filters':{'not_a_filter':True}}):
   with self.assertRaises(ValueError):self.archive.search('float',**kwargs)
if __name__=='__main__':unittest.main()
