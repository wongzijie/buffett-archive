"""Actual MCP stdio initialize, tools/list, search and context round trip."""
import asyncio,json,sys
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
ROOT=Path(__file__).resolve().parents[1]
def payload(result):
 assert not result.isError,result
 if result.structuredContent:return result.structuredContent
 return json.loads(next(c.text for c in result.content if c.type=='text'))
async def main():
 params=StdioServerParameters(command=sys.executable,args=[str(ROOT/'archive.py'),'mcp'])
 async with stdio_client(params) as streams:
  async with ClientSession(*streams) as session:
   await session.initialize();listing=await session.list_tools();names={t.name for t in listing.tools}
   assert {'search_buffett','get_buffett_context','buffett_archive_status'}<=names
   stats=payload(await session.call_tool('buffett_archive_status',{}));assert stats['active_documents']==412
   result=payload(await session.call_tool('search_buffett',{'query':'insurance float','top_k':2,'max_chars':1200}));assert result['results']
   context=payload(await session.call_tool('get_buffett_context',{'chunk_id':result['results'][0]['chunk_id']}));assert context['result']['text']
   print(json.dumps({'pass':True,'tools':sorted(names),'active_documents':stats['active_documents'],'backend':stats['backend']}))
if __name__=='__main__':asyncio.run(main())
