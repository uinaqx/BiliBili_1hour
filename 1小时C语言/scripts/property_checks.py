"""Check meaningful beginner boundaries without executing undefined-behavior examples."""
import json,pathlib,subprocess,sys
sys.stdout.reconfigure(encoding='utf-8');ROOT=pathlib.Path(__file__).resolve().parents[1];folder=ROOT/'build/boundaries';folder.mkdir(parents=True,exist_ok=True)
source=r'''#include <assert.h>
#include <stdio.h>
#include <string.h>
int passed(int score) { return score >= 60; }
int sum_to(int n) { if (n == 0) return 0; return n + sum_to(n - 1); }
void swap(int *a, int *b) { int temp = *a; *a = *b; *b = temp; }
struct Student { char name[16]; int score; };
int main(void) {
    int groups = 0;
    for (int n = 0; n <= 10; n++) {
        assert(sum_to(n) == n * (n + 1) / 2); groups++;
        int total = 0;
        for (int i = 1; i <= n; i++) total += i;
        assert(total == sum_to(n)); groups++;
    }
    int scores[] = {-1, 0, 59, 60, 61, 90, 100};
    for (int i = 0; i < 7; i++) { assert(passed(scores[i]) == (scores[i] >= 60)); groups++; }
    for (int a = -2; a <= 2; a++) for (int b = -2; b <= 2; b++) {
        int x = a, y = b; swap(&x, &y); assert(x == b && y == a); groups++;
    }
    int x = 8; swap(&x, &x); assert(x == 8); groups++;
    int n = 0;
    assert(sscanf("80", "%d", &n) == 1 && n == 80); groups++;
    assert(sscanf("x", "%d", &n) == 0); groups++;
    assert(sscanf("", "%d", &n) == EOF); groups++;
    char name[16] = {0};
    assert(sscanf("abcdefghijklmnopq", "%15s", name) == 1);
    assert(strlen(name) == 15 && name[15] == '\0'); groups++;
    char word[4] = "cat"; assert(strlen(word) == 3 && word[3] == '\0'); groups++;
    int arr[3] = {60, 80, 90}; int total = 0;
    for (int i = 0; i < 3; i++) total += arr[i];
    assert(total == 230); groups++;
    struct Student a = {"Ana", 80}; struct Student b = a;
    b.score = 90; b.name[0] = 'B';
    assert(a.score == 80 && b.score == 90 && a.name[0] == 'A'); groups++;
    printf("%d\n", groups); return 0;
}'''
(folder/'boundary_checks.c').write_text(source,encoding='utf-8')
compiled=subprocess.run(['gcc','-std=c11','-Wall','-Wextra','-Werror','-pedantic','boundary_checks.c','-o','boundary_checks.exe'],cwd=folder,capture_output=True,text=True)
assert compiled.returncode==0,compiled.stderr
ran=subprocess.run([str(folder/'boundary_checks.exe')],cwd=folder,capture_output=True,text=True,timeout=5)
assert ran.returncode==0,ran.stderr
groups=int(ran.stdout);assert groups==62,groups
report=dict(allPassed=True,assertionGroups=groups,categories=['recursion zero and small n','loop bounds and empty range','pass/fail boundaries','swapping including same address','input success, mismatch and EOF','bounded string input and terminator','array sum','independent structure fields'])
(ROOT/'build/property-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('C_BOUNDARIES_PASSED',groups)
