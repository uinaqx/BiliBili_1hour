"""Execute each example from a fresh copy of the course data."""
import json
import pathlib
import re
import sqlite3

ROOT=pathlib.Path(__file__).resolve().parents[1]

def statements(sql):
    buf=''
    for char in sql:
        buf+=char
        if char==';' and sqlite3.complete_statement(buf):
            yield buf.strip()
            buf=''
    assert not buf.strip(), f'Missing semicolon: {buf}'

def display(value):
    return 'NULL' if value is None else str(value)

def verify(chapters):
    seed=(ROOT/'examples/init.sql').read_text(encoding='utf-8-sig')
    records=[]
    for chapter in chapters:
        folder=ROOT/'examples'/chapter['key']
        folder.mkdir(parents=True,exist_ok=True)
        for scene in chapter['scenes']:
            key=scene['key']
            code=scene['code']
            with sqlite3.connect(':memory:',isolation_level=None) as db:
                db.executescript(seed)
                try:
                    cur=None
                    for sql in statements(code):
                        cur=db.execute(sql)
                    if scene['diagnostic']:
                        raise AssertionError((key,'Expected SQL constraint violation'))
                    columns=[x[0] for x in cur.description] if cur and cur.description else []
                    rows=[list(row) for row in cur.fetchall()] if columns else []
                    output=([columns]+rows) if columns else []
                except sqlite3.Error as exc:
                    if not scene['diagnostic'] or scene['diagnostic'] not in str(exc):
                        raise RuntimeError(f'{key}: {exc}') from exc
                    output=[]
                    scene['output']='约束错误 · '+str(exc)
                    scene['outputTable']=None
            expected=scene.get('expected')
            if expected is not None and expected!=rows:
                raise AssertionError((key,expected,rows))
            if output:
                scene['outputTable']=[[display(x) for x in row] for row in output]
                scene['output']='\n'.join(' | '.join(row) for row in scene['outputTable'])
                assert len(rows)<=6,(key,'Result exceeds visual row limit')
            elif 'output' not in scene:
                scene['output']='执行成功'
                scene['outputTable']=None
            (folder/f'{key}.sql').write_text(code+'\n',encoding='utf8')
            records.append(dict(key=key,output=scene['output'],diagnostic=scene['diagnostic']))
    (ROOT/'build/examples-verification.json').write_text(json.dumps(
        dict(sqlite=sqlite3.sqlite_version,examples=records),ensure_ascii=False,indent=2),encoding='utf8')

def main():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('query',type=pathlib.Path)
    args=parser.parse_args()
    seed=(ROOT/'examples/init.sql').read_text(encoding='utf-8-sig')
    with sqlite3.connect(':memory:',isolation_level=None) as db:
        db.executescript(seed)
        for sql in statements(args.query.read_text(encoding='utf-8-sig')):
            data=db.execute(sql)
            if data.description:
                print(' | '.join(x[0] for x in data.description))
                for row in data:
                    print(' | '.join(map(display,row)))

if __name__=='__main__':main()
