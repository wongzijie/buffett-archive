"""Optional CUDA encoder, identical text contract to the archived vectors."""
import threading
MODEL_ID='tencent/WeMM-Embedding-9B'
REVISION='00c52839de57a6d4fd5b78cf5522ccf0ac8ea482'
CONTRACT='wemm-text-rightpad-fp32norm-v2'
class Encoder:
 def __init__(self,model_path=None):
  import torch
  from transformers import AutoModel,AutoProcessor
  if not torch.cuda.is_available():raise ValueError('WeMM backend requires CUDA. Use lexical mode on this machine.')
  if model_path is None:
   from huggingface_hub import snapshot_download
   model_path=snapshot_download(MODEL_ID,revision=REVISION)
  self.torch=torch;self.lock=threading.Lock()
  self.processor=AutoProcessor.from_pretrained(model_path,trust_remote_code=True)
  self.processor.tokenizer.padding_side='right'
  self.model=AutoModel.from_pretrained(model_path,trust_remote_code=True,dtype=torch.bfloat16).cuda().eval()
  self.marker=self.processor.tokenizer.convert_tokens_to_ids('<embedding>')
 def encode(self,texts):
  import numpy as np
  with self.lock,self.torch.inference_mode():
   rendered=[self.processor.apply_chat_template([{'role':'user','content':[{'type':'text','text':t}]}],tokenize=False,add_generation_prompt=False) for t in texts]
   inputs=self.processor(text=rendered,return_tensors='pt',padding=True,truncation=False)
   lengths=inputs['attention_mask'].sum(1)
   if int(lengths.max())>8192:raise ValueError('Input exceeds 8192 model tokens. No silent truncation.')
   last=inputs['input_ids'][self.torch.arange(len(texts)),lengths-1]
   if not self.torch.all(last==self.marker):raise ValueError('Missing final embedding marker')
   vectors=self.model.embedding(**inputs.to('cuda'))[...,:1024].float()
   vectors=self.torch.nn.functional.normalize(vectors,dim=-1).cpu().numpy()
   if not np.isfinite(vectors).all():raise ValueError('Non-finite embeddings')
   return vectors
