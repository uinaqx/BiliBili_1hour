import json,pathlib,tempfile,unittest
from harness import Harness,ScriptedModel,ToolError,IdempotentService,INITIAL,FIRST,FIXED
ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build';BUILD.mkdir(exist_ok=True)
def call(name,args=None,key='test-call'):return dict(type='tool_call',id=key,name=name,arguments={} if args is None else args)
class HarnessTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='harness-case-',dir=BUILD);self.path=pathlib.Path(self.temp.name).resolve();assert self.path.is_relative_to(BUILD.resolve());self.h=Harness(self.path)
    def tearDown(self):
        assert self.path.is_relative_to(BUILD.resolve());self.temp.cleanup()
    def test_full_feedback_loop(self):
        state=self.h.run();self.assertEqual(state['status'],'completed');self.assertEqual(state['events'][2]['result']['stdout'],'FAIL expected=30 actual=10');self.assertEqual(state['events'][4]['result']['stdout'],'PASS expected=30 actual=30');self.assertEqual(self.h.source.read_text(),FIXED)
    def test_invalid_argument_type(self):
        with self.assertRaises(ToolError) as caught:self.h.dispatch(call('read_file',{'path':123}))
        self.assertEqual(caught.exception.code,'INVALID_ARGUMENT')
    def test_unknown_tool(self):
        with self.assertRaises(ToolError) as caught:self.h.dispatch(call('upload_anything'))
        self.assertEqual(caught.exception.code,'UNKNOWN_TOOL')
    def test_missing_field(self):
        with self.assertRaises(ToolError):self.h.dispatch(call('read_file'))
    def test_extra_field(self):
        with self.assertRaises(ToolError):self.h.dispatch(call('run_tests',{'unexpected':True}))
    def test_path_traversal_rejected(self):
        with self.assertRaises(ToolError) as caught:self.h.dispatch(call('read_file',{'path':'../outside.txt'}))
        self.assertEqual(caught.exception.code,'DENIED')
    def test_absolute_outside_rejected(self):
        with self.assertRaises(ToolError):self.h.dispatch(call('read_file',{'path':str(BUILD/'outside.txt')}))
    def test_unauthorized_write_has_no_effect(self):
        h=Harness(self.path,allow_write=False)
        with self.assertRaises(ToolError):h.dispatch(call('apply_patch',{'variant':'fixed'}))
        self.assertEqual(h.source.read_text(),INITIAL)
    def test_reused_call_does_not_repeat_write(self):
        c=call('apply_patch',{'variant':'fixed'});self.h.dispatch(c);r=self.h.dispatch(c);self.assertTrue(r['reused']);self.assertEqual(self.h.state['patchWrites'],1)
    def test_same_id_different_arguments_rejected(self):
        self.h.dispatch(call('apply_patch',{'variant':'first'}))
        with self.assertRaises(ToolError) as caught:self.h.dispatch(call('apply_patch',{'variant':'fixed'}))
        self.assertEqual(caught.exception.code,'ID_CONFLICT')
    def test_pause_and_resume_without_restarting(self):
        self.h.run(pause_after=2);h=Harness(self.path);self.assertEqual(h.state['cursor'],2);state=h.run();self.assertEqual(state['status'],'completed');self.assertEqual(len(state['events']),5);self.assertEqual(state['patchWrites'],2)
    def test_final_is_not_business_success(self):
        state=self.h.run(ScriptedModel(early_final=True));self.assertEqual(state['status'],'rejected_final');self.assertFalse(state['events'][-1]['result']['ok'])
    def test_budget_preserves_partial_artifact(self):
        state=self.h.run(max_turns=2);self.assertEqual(state['status'],'budget_stopped');self.assertEqual(self.h.source.read_text(),FIRST)
    def test_cancel_before_work(self):
        state=self.h.run(cancelled=True);self.assertEqual(state['status'],'cancelled');self.assertEqual(state['events'],[])
    def test_timeout_is_not_success(self):
        h=Harness(self.path,timeout=.000001);r=h.dispatch(call('run_tests'));self.assertFalse(r['ok']);self.assertEqual(r['code'],'TIMEOUT');self.assertEqual(r['status'],'UNKNOWN')
    def test_completed_reload_no_new_side_effects(self):
        self.h.run();h=Harness(self.path);h.run();self.assertEqual(len(h.state['events']),5);self.assertEqual(h.state['patchWrites'],2)
    def test_receiver_stable_id_deduplicates_after_reload(self):
        path=self.path/'receiver.json';one=IdempotentService(path).create('op-17');two=IdempotentService(path).create('op-17');self.assertEqual(one,two);self.assertEqual(len(json.loads(path.read_text())),1)
    def test_different_logical_ids_can_duplicate_effect(self):
        path=self.path/'receiver.json';service=IdempotentService(path);service.create('attempt-1');service.create('attempt-2');self.assertEqual(len(json.loads(path.read_text())),2)
    def test_real_original_fails(self):
        r=self.h.dispatch(call('run_tests'));self.assertFalse(r['ok']);self.assertEqual(r['stdout'],'FAIL expected=30 actual=31')
    def test_tool_result_is_added_to_context(self):
        self.h.run(pause_after=3);last=self.h.state['messages'][-1];self.assertEqual(last['role'],'tool');self.assertEqual(last['callId'],'call-3');self.assertEqual(last['result']['code'],'TEST_FAILED')
if __name__=='__main__':unittest.main(verbosity=2)
