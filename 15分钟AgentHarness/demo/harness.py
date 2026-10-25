"""Deterministic teaching harness. No LLM/API; approved file variants and real tests.

This isolates loop/state/tool behavior for repeatable inspection. Its path policy
is not an OS sandbox and it is not a production agent runtime.
"""
import hashlib,json,pathlib,subprocess,sys,time
INITIAL='def cart_total(values):\n    return sum(values) + 1\n'
FIRST='def cart_total(values):\n    return sum(values[:-1])\n'
FIXED='def cart_total(values):\n    return sum(values)\n'
class ToolError(Exception):
    def __init__(self,code,message):self.code=code;super().__init__(message)
def sha(text):return hashlib.sha256(text.encode('utf8')).hexdigest()
def atomic(path,data):
    temp=path.with_suffix(path.suffix+'.tmp')
    if path.is_symlink() or temp.is_symlink():raise ToolError('DENIED','Unexpected symlink')
    temp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8');temp.replace(path)
class ScriptedModel:
    """Fixed responses, explicitly not an autonomous model intelligence demo."""
    PLAN=[('read_file',{'path':'total.py'}),('apply_patch',{'variant':'first'}),('run_tests',{}),('apply_patch',{'variant':'fixed'}),('run_tests',{})]
    def __init__(self,early_final=False):self.early_final=early_final
    def respond(self,state):
        cursor=state['cursor']
        if cursor>=len(self.PLAN) or self.early_final and cursor>=3:return dict(type='final',text='修复完成')
        name,args=self.PLAN[cursor];return dict(type='tool_call',id=f'call-{cursor+1}',name=name,arguments=args)
class Harness:
    def __init__(self,workspace,allow_write=True,timeout=3):
        self.root=pathlib.Path(workspace).resolve();self.root.mkdir(parents=True,exist_ok=True);self.allow_write=allow_write;self.timeout=timeout;self.path=self.root/'checkpoint.json';self.source=self.root/'total.py'
        if self.source.is_symlink() or self.path.is_symlink():raise ToolError('DENIED','Unexpected symlink')
        if self.path.exists():self.state=json.loads(self.path.read_text(encoding='utf8'))
        else:
            self.source.write_text(INITIAL,encoding='utf8');self.state=dict(cursor=0,turns=0,status='ready',messages=[],events=[],ledger={},patchWrites=0)
            self.save()
    def save(self):atomic(self.path,self.state)
    def validate(self,call):
        if call.get('type')!='tool_call' or not isinstance(call.get('id'),str):raise ToolError('INVALID_CALL','Tool call ID required')
        name=call.get('name');args=call.get('arguments')
        if name not in ['read_file','apply_patch','run_tests']:raise ToolError('UNKNOWN_TOOL','Tool is not registered')
        if not isinstance(args,dict):raise ToolError('INVALID_ARGUMENT','Arguments must be an object')
        expected={'read_file':{'path'},'apply_patch':{'variant'},'run_tests':set()}[name]
        if set(args)!=expected:raise ToolError('INVALID_ARGUMENT','Unexpected or missing fields')
        if name=='read_file':
            if not isinstance(args['path'],str):raise ToolError('INVALID_ARGUMENT','path must be a string')
            target=(self.root/args['path']).resolve()
            if not target.is_relative_to(self.root) or target!=self.source:raise ToolError('DENIED','Path outside the allowed file')
        if name=='apply_patch':
            if not self.allow_write:raise ToolError('DENIED','Writing is not authorized')
            if args['variant'] not in ['first','fixed']:raise ToolError('INVALID_ARGUMENT','Unapproved teaching variant')
        return name,args
    def dispatch(self,call):
        name,args=self.validate(call);fingerprint=sha(json.dumps([name,args],sort_keys=True));old=self.state['ledger'].get(call['id'])
        if old:
            if old['fingerprint']!=fingerprint:raise ToolError('ID_CONFLICT','Same call ID with different arguments')
            return dict(old['result'],reused=True)
        if name=='read_file':result=dict(ok=True,content=self.source.read_text(encoding='utf8'))
        elif name=='apply_patch':
            content=FIRST if args['variant']=='first' else FIXED;self.source.write_text(content,encoding='utf8');self.state['patchWrites']+=1;result=dict(ok=True,sourceSha256=sha(content),content=content)
        else:
            test="from total import cart_total\nactual=cart_total([10,20])\nprint(('PASS' if actual==30 else 'FAIL')+f' expected=30 actual={actual}')\nraise SystemExit(0 if actual==30 else 1)\n"
            try:
                p=subprocess.run([sys.executable,'-B','-c',test],cwd=self.root,capture_output=True,text=True,encoding='utf8',timeout=self.timeout)
                result=dict(ok=p.returncode==0,exitCode=p.returncode,stdout=p.stdout.strip(),code='OK' if p.returncode==0 else 'TEST_FAILED')
            except subprocess.TimeoutExpired:result=dict(ok=False,code='TIMEOUT',status='UNKNOWN',message='No success was confirmed')
        self.state['ledger'][call['id']]=dict(fingerprint=fingerprint,result=result)
        self.state['events'].append(dict(sequence=len(self.state['events'])+1,callId=call['id'],tool=name,arguments=args,result=result,sourceSha256=sha(self.source.read_text(encoding='utf8'))))
        return result
    def run(self,model=None,max_turns=6,pause_after=None,cancelled=False):
        model=model or ScriptedModel()
        if self.state['status']=='completed':return self.state
        performed=0
        while self.state['turns']<max_turns:
            if cancelled:self.state['status']='cancelled';self.save();return self.state
            self.state['turns']+=1;reply=model.respond(self.state)
            if reply['type']=='final':
                last=self.state['events'][-1] if self.state['events'] else None
                accepted=last and last['tool']=='run_tests' and last['result']['ok'] and self.source.read_text(encoding='utf8')==FIXED
                self.state['status']='completed' if accepted else 'rejected_final';self.state['final']=reply['text'];self.save();return self.state
            try:result=self.dispatch(reply)
            except ToolError as e:result=dict(ok=False,code=e.code,message=str(e))
            self.state['messages'].extend([dict(role='assistant',toolCall=reply),dict(role='tool',callId=reply['id'],result=result)])
            self.state['cursor']+=1;performed+=1;self.state['status']='running';self.save()
            if pause_after is not None and performed>=pause_after:self.state['status']='paused';self.save();return self.state
        self.state['status']='budget_stopped';self.save();return self.state
class IdempotentService:
    """Local teaching stand-in for a receiver that honors stable operation IDs."""
    def __init__(self,path):self.path=pathlib.Path(path)
    def create(self,operation_id):
        data=json.loads(self.path.read_text(encoding='utf8')) if self.path.exists() else {}
        if operation_id not in data:data[operation_id]=dict(ticket=f'ticket-{len(data)+1}');atomic(self.path,data)
        return data[operation_id]
def main():
    root=pathlib.Path(__file__).resolve().parents[1];work=root/'build/demo-run';work.mkdir(parents=True,exist_ok=True);h=Harness(work);state=h.run();assert state['status']=='completed'
    report=dict(model='scripted deterministic responses, no LLM call',fileAndTests='real local execution',status=state['status'],input=[10,20],expected=30,initial=INITIAL,firstPatch=FIRST,final=FIXED,events=state['events'],messages=state['messages'],checkpoint=state)
    (root/'build/demo-execution.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print('DEMO_COMPLETED',[(e['tool'],e['result'].get('stdout',e['result']['ok'])) for e in state['events']],flush=True)
if __name__=='__main__':main()
