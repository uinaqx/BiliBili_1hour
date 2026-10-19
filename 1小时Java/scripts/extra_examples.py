"""Companion enhanced-for variant mentioned in the narration."""
import json,pathlib,subprocess,sys
from java_tools import command
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'out/Java示例/07-extra-enhanced-for';OUT.mkdir(parents=True,exist_ok=True)
SOURCE='''public class Main {
    public static void main(String[] args) {
        int[] scores = {60, 80, 100};
        int total = 0;
        for (int score : scores) {
            total += score;
        }
        System.out.println(total);
        System.out.println(total / 3.0);
    }
}
'''
(OUT/'Main.java').write_text(SOURCE,encoding='utf-8');temp=ROOT/'build/extra-example';temp.mkdir(exist_ok=True)
subprocess.run([command('javac'),'-encoding','UTF-8','--release','21','-Xlint:all','-Werror','-d',str(temp),str(OUT/'Main.java')],check=True)
actual=subprocess.check_output([command('java'),'-cp',str(temp),'Main'],encoding='utf-8').replace('\r\n','\n');assert actual=='240\n80.0\n'
(OUT/'预期行为.json').write_text(json.dumps(dict(kind='run',expected=actual,allPassed=True),indent=2,ensure_ascii=False),encoding='utf-8');print('ENHANCED_FOR_VERIFIED')
