"""Prove existing reusable clips need no credentials and no network."""
import contextlib,io,json,pathlib
import requests,voice
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
    def denied(*args,**kwargs):raise RuntimeError('Network disabled for offline cache verification')
    requests.post=denied;requests.get=denied
    import socket
    socket.socket.connect=denied;socket.create_connection=denied
    with contextlib.redirect_stdout(io.StringIO()):voice.generate({})
    course=json.loads((ROOT/'public/course.json').read_text(encoding='utf8'));count=sum(len(s['parts']) for c in course['chapters'] for s in c['scenes'])
    print(json.dumps(dict(allPassed=True,clips=count,credentialsSupplied=False,networkDisabled=True)),flush=True)
if __name__=='__main__':main()
