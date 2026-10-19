"""Exercise the displayed binary search and sorts against standard-library results."""
import json,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.stdout.reconfigure(encoding='utf-8')
m={x['key']:x for x in json.loads((ROOT/'content/example_manifest.json').read_text(encoding='utf-8'))}
search=m['09-02']['source'].split('int main(){')[0]
merge=m['10-03']['source'].split('int main(){')[0].split('using namespace std;')[1]
partition=m['10-04']['source'].split('int main(){')[0].split('using namespace std;')[1]
insertion=m['10-02']['source'].split('int main(){')[1].split('for (int x:a)')[0]
insertion=insertion[insertion.index('for (int i=1;'):]
source=search+merge+partition+'\n#include <random>\nint main(){\n'+r'''
    mt19937 rng(20261017); int checks=0;
    for(int n=0;n<=64;++n) for(int trial=0;trial<20;++trial){
        vector<int> input(n);for(int& x:input)x=int(rng()%13)-6;
        vector<int> expected=input;sort(expected.begin(),expected.end());
        vector<int> a=input;mergeSort(a,0,a.size());assert(a==expected);++checks;
        a=input;
'''+insertion+r'''
        assert(a==expected);++checks;
        for(int target=-8;target<=8;++target){
            auto p=lower_bound(expected.begin(),expected.end(),target);
            int want=(p==expected.end()||*p!=target)?-1:int(p-expected.begin());
            assert(findIndex(expected,target)==want);++checks;
        }
        if(n){
            a=input;int pivot=input.back();int k=partitionOnce(a,0,n);
            assert(a[k]==pivot);
            for(int i=0;i<k;++i)assert(a[i]<pivot);
            for(int i=k+1;i<n;++i)assert(a[i]>=pivot);
            sort(a.begin(),a.end());assert(a==expected);++checks;
        }
    }
    cout << checks << "\n";
}
'''
p=ROOT/'build/property-checks.cpp';exe=p.with_suffix('.exe');p.write_text(source,encoding='utf-8')
subprocess.run(['g++','-std=c++14','-O2',str(p),'-o',str(exe)],check=True)
r=subprocess.run([str(exe)],capture_output=True,text=True,check=True)
report=dict(allPassed=True,assertionGroups=int(r.stdout),sizes='0..64',trialsPerSize=20,checks=['first-match binary search versus lower_bound','merge sort versus std::sort','insertion sort versus std::sort','partition pivot, sides and element preservation'])
(ROOT/'build/property-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('PROPERTY_CHECKS_PASSED',report['assertionGroups'])
