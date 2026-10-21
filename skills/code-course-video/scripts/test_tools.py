"""Behavioral regression tests in disposable directories; no account or TTS access."""
import copy,json,os,pathlib,shutil,struct,subprocess,sys,tempfile,unittest,zipfile,zlib
import timeline_tools as timeline
import safe_delivery as delivery
import media_qa as media

ASSETS=pathlib.Path(__file__).resolve().parents[1]/'assets'

class TimelineTests(unittest.TestCase):
    def setUp(self):self.course=timeline.read(ASSETS/'course.example.json');self.words=timeline.read(ASSETS/'words.example.json')
    def test_valid_example_and_final_onsets(self):
        self.assertTrue(timeline.validate(self.course)['allPassed'])
        out,report=timeline.resolve(self.course,timeline.read(ASSETS/'anchors.example.json'),ASSETS)
        self.assertTrue(report['allPassed'],report);self.assertEqual([c['beginFrame'] for c in out['scenes'][0]['codeCues']],[12,72])
        self.assertFalse(report['alignment'][0]['audioIdentityVerified'])
    def test_reject_empty_or_wrong_initial(self):
        for lines in [[],[3],[0]]:
            c=copy.deepcopy(self.course);c['scenes'][0]['initialCodeLines']=lines
            self.assertFalse(timeline.validate(c)['allPassed'])
    def test_panel_isolation_and_crossing_phrase(self):
        c=copy.deepcopy(self.course);s=c['scenes'][0];s['panels']=[{'id':'new','beginFrame':200,'code':'print(10)','initialCodeLines':[1]}]
        s['codeCues']=[{'beginFrame':250,'lines':[2],'panelId':'root'}]
        self.assertFalse(timeline.validate(c)['allPassed'])
        s['codeCues']=[{'beginFrame':190,'endFrame':210,'lines':[1]}]
        self.assertFalse(timeline.validate(c)['allPassed'])
    def test_caption_overlap_and_thinking_hold(self):
        c=copy.deepcopy(self.course);c['scenes'][0]['captions'][1]['start']=1.0
        self.assertFalse(timeline.validate(c)['allPassed'])
        c=copy.deepcopy(self.course);c['scenes'][0].update(kind='question',speechFrames=300,holdSeconds=4)
        self.assertFalse(timeline.validate(c)['allPassed'])
    def test_ambiguity_missing_and_token_boundary(self):
        words={'timeBase':'final-audio','timeUnit':'seconds','words':[{'text':'输出结果','start':0,'end':1},{'text':'输出结果','start':2,'end':3}]}
        with self.assertRaisesRegex(ValueError,'ambiguous'):timeline.phrase_time(words,{'phrase':'输出结果'})
        self.assertEqual(timeline.phrase_time(words,{'phrase':'输出结果','occurrence':2}),(2.0,3.0))
        with self.assertRaisesRegex(ValueError,'not found'):timeline.phrase_time(words,{'phrase':'不存在'})
        with self.assertRaisesRegex(ValueError,'inside'):timeline.phrase_time(words,{'phrase':'结果','occurrence':1})
    def test_changed_audio_and_unspecified_timebase(self):
        with self.assertRaises(ValueError):timeline.phrase_time({'words':[]},{'phrase':'a'})
        with tempfile.TemporaryDirectory() as folder:
            root=pathlib.Path(folder);(root/'audio.wav').write_bytes(b'changed final audio')
            words=copy.deepcopy(self.words);words['audioSha256']='0'*64;timeline.write(root/'words.json',words)
            c=copy.deepcopy(self.course);c['scenes'][0]['audio']='audio.wav'
            plan={'scenes':{'arrays-demo':{'audioMeta':'words.json','cues':[]}}}
            _,report=timeline.resolve(c,plan,root);self.assertFalse(report['allPassed']);self.assertIn('hash differs',' '.join(report['errors']))
    def test_diagram_patch_does_not_expire(self):
        c=copy.deepcopy(self.course);s=c['scenes'][0];s['diagramObjectIds']=['alu']
        s['diagramCues']=[{'beginFrame':60,'patch':{'focus':'alu','result':20}}]
        self.assertTrue(timeline.validate(c)['allPassed'])
        s['diagramCues'][0]['endFrame']=70;self.assertFalse(timeline.validate(c)['allPassed'])
    def test_failed_resolution_does_not_write_output(self):
        with tempfile.TemporaryDirectory() as folder:
            p=pathlib.Path(folder);plan=timeline.read(ASSETS/'anchors.example.json');plan['scenes']['arrays-demo']['cues'][0]['phrase']='找不到的短语';timeline.write(p/'anchors.json',plan)
            r=subprocess.run([sys.executable,'-X','utf8',str(pathlib.Path(timeline.__file__)),'resolve',str(ASSETS/'course.example.json'),str(p/'anchors.json'),'--root',str(ASSETS),'--output',str(p/'partial.json')],capture_output=True)
            self.assertNotEqual(r.returncode,0);self.assertFalse((p/'partial.json').exists())

class DeliveryTests(unittest.TestCase):
    def test_secret_across_chunk_boundary_is_not_echoed(self):
        with tempfile.TemporaryDirectory() as folder:
            p=pathlib.Path(folder);secret=('sk-'+'x'*40).encode();(p/'bad.txt').write_bytes(b' '*((1024*1024)-8)+secret)
            report=delivery.scan(p);self.assertFalse(report['allPassed']);self.assertNotIn(secret.decode(),json.dumps(report))
    def test_zip_env_path_and_configured_secret(self):
        with tempfile.TemporaryDirectory() as folder:
            p=pathlib.Path(folder);key=b'private-workspace-value'
            with zipfile.ZipFile(p/'bad.zip','w') as z:z.writestr('../escape.txt',b'hello');z.writestr('app/.env',b'config');z.writestr('app/meta.json',key)
            report=delivery.scan(p/'bad.zip',[('TEST_VALUE',key)]);self.assertFalse(report['allPassed'])
            reasons={i['reason'] for i in report['issues']};self.assertIn('unsafe-archive-path',reasons);self.assertIn('real-env-file',reasons);self.assertIn('configured-secret:TEST_VALUE',reasons)
            self.assertNotIn(key.decode(),json.dumps(report))
    def test_allowlist_pack_omits_env_and_dependencies(self):
        with tempfile.TemporaryDirectory() as folder:
            p=pathlib.Path(folder);root=p/'工程';(root/'src').mkdir(parents=True);(root/'src/main.py').write_text('print(1)',encoding='utf-8');(root/'.env').write_text('private',encoding='utf-8')
            (root/'node_modules').mkdir();(root/'node_modules/cache').write_text('not needed')
            report=delivery.pack(root,['src'],p/'course.zip');self.assertTrue(report['allPassed'])
            with zipfile.ZipFile(p/'course.zip') as z:self.assertEqual(z.namelist(),['工程/src/main.py']);self.assertIsNone(z.testzip())
    def test_missing_scan_target_and_escape_include_fail(self):
        with tempfile.TemporaryDirectory() as folder:
            p=pathlib.Path(folder)
            with self.assertRaises(ValueError):delivery.scan(p/'missing')
            with self.assertRaises(ValueError):delivery.pack(p,['../outside'],p/'course.zip')

def png(path,rgb):
    def chunk(kind,data):return struct.pack('!I',len(data))+kind+data+struct.pack('!I',zlib.crc32(kind+data)&0xffffffff)
    raw=(b'\x00'+bytes(rgb)*64)*64
    path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',64,64,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))

@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),'FFmpeg required for media tests')
class MediaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='course-qa-');cls.root=pathlib.Path(cls.temp.name)
        for name,color in [('red',(255,0,0)),('green',(0,255,0)),('blue',(0,0,255))]:png(cls.root/(name+'.png'),color)
        (cls.root/'frames.ffconcat').write_text("ffconcat version 1.0\nfile 'red.png'\noption framerate 30\nduration 0.6\nfile 'green.png'\noption framerate 30\nduration 0.9\nfile 'blue.png'\noption framerate 30\nduration 0.7\nfile 'blue.png'\noption framerate 30\n",encoding='utf-8')
        cls.video=cls.root/'fixture.mp4'
        subprocess.run(['ffmpeg','-nostdin','-y','-v','error','-f','concat','-safe','0','-i',str(cls.root/'frames.ffconcat'),'-f','lavfi','-i','anullsrc=r=48000:cl=mono','-t','2.2','-fps_mode','vfr','-c:v','libx264','-bf','2','-pix_fmt','yuv420p','-c:a','aac',str(cls.video)],check=True)
    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()
    def test_vfr_displayed_frame_including_b_frames(self):
        result=media.extract(self.video,[.4,1.0,1.8],self.root/'evidence')
        for row,channel in zip(result['frames'],[0,1,2]):
            pixel=subprocess.check_output(['ffmpeg','-v','error','-i',row['image'],'-vf','scale=1:1','-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','-'])
            self.assertGreater(pixel[channel],200);self.assertLess(row['displayPtsSeconds'],row['requestedSeconds']+.001)
    def test_media_integrity_and_audio_change_detection(self):
        report=media.verify(self.video,self.video,True,True);self.assertTrue(report['allPerformedChecksPassed']);self.assertIn('burned-in subtitle visibility',report['notChecked'])
        changed=self.root/'changed.mp4'
        subprocess.run(['ffmpeg','-nostdin','-y','-v','error','-i',str(self.video),'-f','lavfi','-i','sine=frequency=500:sample_rate=48000','-map','0:v:0','-map','1:a:0','-t','2.2','-c:v','copy','-c:a','aac',str(changed)],check=True)
        self.assertFalse(media.verify(changed,self.video,True)['checks']['audioBitstreamIdentical'])

if __name__=='__main__':unittest.main(verbosity=2)
