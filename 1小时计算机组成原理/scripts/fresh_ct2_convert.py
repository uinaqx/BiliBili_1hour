"""Offline conversion of the existing Whisper base weights to CPU int8.

Weight-name mapping follows Hugging Face's Apache-2.0 conversion utility:
https://github.com/huggingface/transformers/blob/v4.40.2/src/transformers/models/whisper/convert_openai_to_hf.py
Only small configuration/tokenizer files are downloaded; no model weights.
"""
import argparse,json,pathlib,shutil,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
BASE=ROOT/'build/fresh-subtitles-20261019';HF=BASE/'base-hf';CT2=BASE/'base-ct2'
MAPPING={'blocks':'layers','mlp.0':'fc1','mlp.2':'fc2','mlp_ln':'final_layer_norm',
 '.attn.query':'.self_attn.q_proj','.attn.key':'.self_attn.k_proj','.attn.value':'.self_attn.v_proj',
 '.attn_ln':'.self_attn_layer_norm','.attn.out':'.self_attn.out_proj',
 '.cross_attn.query':'.encoder_attn.q_proj','.cross_attn.key':'.encoder_attn.k_proj',
 '.cross_attn.value':'.encoder_attn.v_proj','.cross_attn_ln':'.encoder_attn_layer_norm',
 '.cross_attn.out':'.encoder_attn.out_proj','decoder.ln.':'decoder.layer_norm.',
 'encoder.ln.':'encoder.layer_norm.','token_embedding':'embed_tokens',
 'encoder.positional_embedding':'encoder.embed_positions.weight',
 'decoder.positional_embedding':'decoder.embed_positions.weight','ln_post':'layer_norm'}

def download(name):
    import requests
    p=HF/name
    if p.exists() and p.stat().st_size>0:return
    r=requests.get('https://huggingface.co/openai/whisper-base/resolve/main/'+name,timeout=40)
    r.raise_for_status();p.write_bytes(r.content);print('BASE_CONFIG',name,len(r.content),flush=True)

def prepare():
    import torch
    from transformers import WhisperConfig,WhisperForConditionalGeneration,GenerationConfig
    HF.mkdir(parents=True,exist_ok=True)
    for name in ['config.json','generation_config.json','preprocessor_config.json']:download(name)
    tok=BASE/'asr/small-model/tokenizer.json'
    if tok.exists():shutil.copy2(tok,HF/'tokenizer.json')
    else:download('tokenizer.json')
    if not (HF/'model.safetensors').exists():
        checkpoint=pathlib.Path.home()/'.cache/whisper/base.pt'
        raw=torch.load(checkpoint,map_location='cpu',weights_only=True)
        state={}
        for key,value in raw['model_state_dict'].items():
            new=key
            for before,after in MAPPING.items():
                if before in key:new=new.replace(before,after)
            state['model.'+new]=value
        state['proj_out.weight']=state['model.decoder.embed_tokens.weight']
        config=WhisperConfig.from_pretrained(HF,local_files_only=True)
        model=WhisperForConditionalGeneration(config)
        model.load_state_dict(state,strict=True)
        model.generation_config=GenerationConfig.from_pretrained(HF,local_files_only=True)
        model.half().save_pretrained(HF,safe_serialization=True)
        print('HF_BASE_WEIGHTS_READY',flush=True)

def convert():
    import ctranslate2
    converter=ctranslate2.converters.TransformersConverter(str(HF),copy_files=['tokenizer.json','preprocessor_config.json'])
    converter.convert(str(CT2),quantization='int8',force=True)
    print('CT2_BASE_INT8_READY',CT2,flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--prepare-only',action='store_true');args=p.parse_args()
    prepare()
    if not args.prepare_only:convert()
