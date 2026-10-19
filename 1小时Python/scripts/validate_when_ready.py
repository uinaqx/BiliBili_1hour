"""Resume final media validation as soon as the atomically published MP4 appears."""
import pathlib,subprocess,sys,time
ROOT=pathlib.Path(__file__).resolve().parents[1];FINAL=ROOT/'out/一小时学习Python_零基础.mp4'
deadline=time.monotonic()+3600
while not FINAL.exists():
    if time.monotonic()>deadline:raise TimeoutError('Final video not available')
    time.sleep(4)
for name in ('check.py','final_frames.py'):
    subprocess.run([sys.executable,'-X','utf8','scripts/'+name],cwd=ROOT,check=True)
print('FINAL_MEDIA_CHECKS_DONE',flush=True)
