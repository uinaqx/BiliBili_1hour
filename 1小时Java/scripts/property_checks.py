"""Exercise meaningful Java boundaries and state changes, without online calls."""
import json,pathlib,subprocess,sys
from java_tools import command
sys.stdout.reconfigure(encoding='utf-8');ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'build/properties';OUT.mkdir(parents=True,exist_ok=True)
SOURCE=r'''import java.util.ArrayList;
import java.util.HashMap;
public class Main {
    static int groups=0;
    static void check(boolean ok) { if(!ok)throw new AssertionError("Group "+(groups+1)); groups++; }
    static boolean passed(int n) {return n>=60;}
    static String level(int n) {if(n>=90)return "excellent";else if(n>=60)return "pass";else return "retry";}
    static int sum(int n) {int total=0;for(int i=1;i<=n;i++)total+=i;return total;}
    static void addFive(int value) {value+=5;}
    static int returnedFive(int value) {return value+5;}
    static class Student {
        private int score;
        Student(int score){this.score=score;}
        int getScore(){return score;}
        void setScore(int score){this.score=score;}
    }
    static void change(Student s) {s.setScore(90);}
    static void reassign(Student s) {s=new Student(10);}
    static int requireScore(int n) {if(n<0||n>100)throw new IllegalArgumentException("bad score");return n;}
    static String route(String text){String r="A ";try{Integer.parseInt(text);r+="B ";}catch(NumberFormatException e){r+="C ";}return r+"D";}
    public static void main(String[] args) {
        int a=3,b=8;a=b;b=9;check(a==8&&b==9);
        check(7/2==3&&7.0/2==3.5);double d=7/2;check(d==3.0);
        check(("sum="+3+5).equals("sum=35")&&("sum="+(3+5)).equals("sum=8"));
        check(!passed(59)&&passed(60)&&passed(61));
        check(level(59).equals("retry")&&level(60).equals("pass"));
        check(level(89).equals("pass")&&level(90).equals("excellent")&&level(100).equals("excellent"));
        check(sum(0)==0&&sum(1)==1&&sum(3)==6&&sum(100)==5050);
        int n=0,doCount=0;do{doCount++;}while(n>0);check(doCount==1);
        String shown="";for(int i=1;i<=5;i++){if(i==3)continue;shown+=i;}check(shown.equals("1245"));
        int[] values={60,80,100};int total=0;for(int i=0;i<values.length;i++)total+=values[i];check(total==240&&(double)total/values.length==80.0);
        int enhanced=0;for(int v:values)enhanced+=v;check(enhanced==total);
        check(values[0]==60&&values[values.length-1]==100);
        boolean badIndex=false;try{int unused=values[values.length];System.out.print(unused);}catch(ArrayIndexOutOfBoundsException e){badIndex=true;}check(badIndex);
        int[] empty={};boolean accessed=false;if(empty.length>0){accessed=true;System.out.print(empty[empty.length-1]);}check(!accessed);
        check(new int[3][0].length==3);int[] zeroes=new int[3];check(zeroes[0]==0&&zeroes[2]==0);
        String name="Ana",upper=name.toUpperCase();check(name.equals("Ana")&&upper.equals("ANA"));
        check(name.length()==3&&name.charAt(0)=='A'&&name.substring(1,3).equals("na"));
        String same=new String("Ana");check(name.equals(same)&&name!=same);
        int score=80;addFive(score);check(score==80);score=returnedFive(score);check(score==85);
        Student first=new Student(80),alias=first;alias.setScore(90);check(first.getScore()==90);
        Student other=new Student(first.getScore());other.setScore(70);check(first.getScore()==90&&other.getScore()==70);
        change(other);check(other.getScore()==90);reassign(other);check(other.getScore()==90);
        ArrayList<String> names=new ArrayList<>();names.add("Ana");names.add("Bo");names.remove(0);check(names.size()==1&&names.get(0).equals("Bo"));
        names.add("Cy");check(names.size()==2&&names.get(1).equals("Cy"));
        ArrayList<Integer> list=new ArrayList<>();list.add(80);list.add(90);list.set(0,85);check(list.size()==2&&list.get(0)==85);
        HashMap<String,Integer> map=new HashMap<>();map.put("Ana",80);map.put("Ana",85);check(map.size()==1&&map.get("Ana")==85);
        check(!map.containsKey("Cy")&&map.getOrDefault("Cy",0)==0&&!map.containsKey("Cy"));
        map.put("Zero",0);check(map.containsKey("Zero")&&map.getOrDefault("Zero",0)==0);
        check(requireScore(0)==0&&requireScore(60)==60&&requireScore(100)==100);
        int rejected=0;for(int x:new int[]{-1,101}){try{requireScore(x);}catch(IllegalArgumentException e){rejected++;}}check(rejected==2);
        check(route("abc").equals("A C D")&&route("80").equals("A B D"));
        System.out.println("PROPERTY_GROUPS="+groups);
    }
}'''
def main():
    (OUT/'Main.java').write_text(SOURCE,encoding='utf-8')
    subprocess.run([command('javac'),'-encoding','UTF-8','--release','21','-Xlint:all','-Werror',str(OUT/'Main.java')],check=True)
    result=subprocess.check_output([command('java'),'-ea','-cp',str(OUT),'Main'],encoding='utf-8').strip()
    count=int(result.split('=')[1]);report=dict(allPassed=True,assertionGroups=count,scope='boundaries, loops, arrays, strings, parameter values, object identity, collection changes and exception routes')
    (ROOT/'build/property-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print('JAVA_PROPERTIES_PASSED',count,flush=True)
if __name__=='__main__':main()
