"""Auditable word-only spelling fixes for fresh audio recognition.

All edits are explicitly reviewed against new ASR and lecture vocabulary.
The source JSON and timestamps remain unchanged; consumer applies replacements.
"""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'build/fresh-subtitles-20261019'
OUT=BASE/'text'

def dump(value):
    OUT.mkdir(parents=True,exist_ok=True)
    path=OUT/'corrections.json';tmp=path.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8');tmp.replace(path)

def make_corrections(specs, reviewed, phrases=None):
    corrections=[]
    for chunk,segment,word,original,replacement,reason in specs:
        filename=f'chunk-{chunk:03}.json'
        data=json.loads((BASE/'asr'/filename).read_text(encoding='utf-8'))
        source=data['segments'][segment]['words'][word]
        assert source['word']==original,(filename,segment,word,source['word'],original)
        corrections.append({'chunk_file':filename,'segment_index':segment,'word_index':word,
                            'original':original,'replacement':replacement,'reason':reason,
                            'confidence':'high','start':source['start'],'end':source['end'],
                            'timing_unchanged':True})
    for chunk, phrase_rules in (phrases or {}).items():
        filename=f'chunk-{chunk:03}.json'
        data=json.loads((BASE/'asr'/filename).read_text(encoding='utf-8'))
        for si,seg in enumerate(data['segments']):
            words=seg.get('words',[]); text=''.join(w['word'] for w in words)
            revised=text;reasons=[]
            for original,replacement,reason in phrase_rules:
                assert len(original)==len(replacement),(original,replacement)
                if original in revised: revised=revised.replace(original,replacement);reasons.append(reason)
            cursor=0
            for wi,w in enumerate(words):
                new=revised[cursor:cursor+len(w['word'])];cursor+=len(w['word'])
                if new==w['word']:continue
                corrections.append({'chunk_file':filename,'segment_index':si,'word_index':wi,
                    'original':w['word'],'replacement':new,'reason':'；'.join(reasons),
                    'confidence':'high','start':w['start'],'end':w['end'],'timing_unchanged':True})
    dump({'source':'fresh audio ASR only; no prior subtitle data',
          'reviewed_chunks':reviewed,'corrections':corrections,'uncertain':[]})

if __name__=='__main__':
    make_corrections([
        (0,1,37,'处','储','存储器术语同音字'),
        (0,2,16,'基','计','计组为计算机组成原理简称'),
        (0,4,14,'会','汇','写汇编语境同音字'),
        (0,4,18,'被','背','背芯片型号语境同音字'),
        (0,5,12,'力,','例,','小算例术语同音字'),
        (0,6,0,'徐','学','学完以后语境识别错误'),
        (0,6,1,'万','完','学完以后语境识别错误'),
        (0,9,2,'指','纸','准备纸笔语境同音字'),
        (0,12,0,'在','再','再往上语境同音字'),
        (0,12,1,'网','往','再往上语境同音字'),
        (0,13,1,'著,','着,','接着用字统一'),
        (0,24,1,'字','次','一次传输语境识别错误'),
        (0,25,0,'确','缺','缺失代价术语同音字'),
        (0,25,1,'实','失','缺失代价术语同音字'),
        (0,26,3,'独','读','读清题意语境同音字'),
        (0,26,4,'卿','清','读清题意语境同音字'),
        (0,26,5,'提','题','读清题意语境同音字'),
        (0,26,6,'议','意','读清题意语境同音字'),
        (0,30,2,'计','记','记答案语境同音字'),
    ],list(range(2)),{
        1:[('分轻','分清','分清语境同音字'),('整书','整数','无符号整数术语'),
           ('小鞋','小写','单位大小写'),('大鞋','大写','单位大小写'),
           ('宽堵','宽度','数据宽度术语'),('同一词','同义词','同义词同音字'),
           ('实境制','十进制','十进制术语'),('各位','个位','十进制个位'),
           ('这是梅王','只是每往','每往左一格语境'),('相家','相加','权重相加'),
           ('禁制','进制','进制术语'),(' 生',' 剩','取值后余数语境'),
           ('很常识','很长时','二进制位数很长的语境'),('协法','写法','写法同音字'),
           ('字母帝','字母D','十六进制字母D')],
    })
