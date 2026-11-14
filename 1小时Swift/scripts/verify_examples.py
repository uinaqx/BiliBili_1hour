import concurrent.futures
import json
import os
import pathlib
import shutil
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]

def swift_environment():
    environment = os.environ.copy()
    compiler = shutil.which('swiftc')
    if os.name == 'nt':
        install = pathlib.Path(os.environ['LOCALAPPDATA']) / 'Programs/Swift'
        if not compiler:
            choices = sorted(install.glob('Toolchains/*/usr/bin/swiftc.exe'), reverse=True)
            compiler = str(choices[0]) if choices else None
        if compiler:
            runtime = sorted(install.glob('Runtimes/*/usr/bin'), reverse=True)
            environment['PATH'] = os.pathsep.join([str(pathlib.Path(compiler).parent),
                *(str(p) for p in runtime), environment['PATH']])
        if not environment.get('SDKROOT'):
            sdks = sorted(install.glob('Platforms/*/Windows.platform/Developer/SDKs/Windows.sdk'), reverse=True)
            if sdks:
                environment['SDKROOT'] = str(sdks[0])
    if not compiler:
        raise RuntimeError('Swift compiler unavailable')
    return compiler, environment

def run(args, cwd, env, data=None):
    return subprocess.run(args, cwd=cwd, env=env, text=True, encoding='utf-8',
                          errors='replace', input=data, capture_output=True, timeout=120)

def compile_swift(compiler, source, exe, cwd, env):
    if pathlib.Path(compiler).name.lower() == 'swift-frontend.exe':
        obj = source.with_suffix('.obj')
        compiled = run([compiler, '-emit-object', '-swift-version', '6',
                        '-target', 'x86_64-unknown-windows-msvc',
                        '-sdk', env['SDKROOT'], str(source), '-o', str(obj)], cwd, env)
        if compiled.returncode:
            return compiled
        clang = pathlib.Path(compiler).with_name('clang.exe')
        libs = pathlib.Path(env['SDKROOT'])/'usr/lib/swift/windows/x86_64'
        return run([str(clang), '-fuse-ld=lld', str(obj), str(libs/'swiftrt.obj'), f'-L{libs}', '-lswiftCore',
                    '-o', str(exe)], cwd, env)
    return run([compiler, '-swift-version', '6', str(source), '-o', str(exe)], cwd, env)

def verify_scene(scene, temp, compiler, env):
    key = scene['key']
    cwd = temp / key
    cwd.mkdir()
    source = cwd / 'main.swift'
    exe = cwd / ('example.exe' if os.name == 'nt' else 'example')
    output_dir = ROOT / 'examples' / scene['chapterKey'] / key
    output_dir.mkdir(parents=True, exist_ok=True)
    if scene['diagnostic']:
        source.write_text(scene['code']+'\n', encoding='utf-8')
        (output_dir/'compile-error.swift').write_bytes(source.read_bytes())
        invalid = compile_swift(compiler, source, exe, cwd, env)
        if invalid.returncode == 0 or scene['diagnostic'] not in invalid.stderr:
            raise AssertionError((key, 'expected diagnostic', invalid.stderr))
    source.write_text((scene['answerCode'] or scene['code'])+'\n', encoding='utf-8')
    (output_dir/'main.swift').write_bytes(source.read_bytes())
    built = compile_swift(compiler, source, exe, cwd, env)
    if built.returncode:
        raise AssertionError((key, 'compile error', built.stderr))
    result = run([str(exe)], cwd, env, scene['fixtures'].get('stdin', ''))
    expected = scene['output'].replace('\\n', '\n')
    if result.returncode or result.stdout.rstrip('\n') != expected:
        raise AssertionError((key, 'output differs', result.returncode, result.stdout, expected, result.stderr))
    (output_dir/'expected.txt').write_text(expected+'\n', encoding='utf-8')
    if 'stdin' in scene['fixtures']:
        (output_dir/'input.txt').write_text(scene['fixtures']['stdin'], encoding='utf-8')
    print('EXAMPLE_OK', key, flush=True)
    return dict(key=key, output=expected, expectedCompileError=scene['diagnostic'])

def verify_project(temp, compiler, env):
    cwd = temp / 'project'
    cwd.mkdir()
    source = cwd / 'main.swift'
    shutil.copyfile(ROOT/'examples/完整项目/main.swift', source)
    exe = cwd / ('expense.exe' if os.name=='nt' else 'expense')
    built = compile_swift(compiler, source, exe, cwd, env)
    assert built.returncode==0,built.stderr
    first = run([str(exe)], cwd, env, '1\n午餐\n1800\n1\n车票\n300\n2\n3\n1\n0\n')
    assert first.returncode == 0 and '总额：2100 分' in first.stdout and '已删除 午餐' in first.stdout,first.stdout
    second = run([str(exe)], cwd, env, '2\n3\n0\n1\n错误\nabc\n2\n0\n')
    assert second.returncode == 0 and '1. 车票 300 分' in second.stdout and '编号无效' in second.stdout
    assert '请输入 1 到 1000000 分的整数' in second.stdout and '总额：300 分' in second.stdout
    file = cwd/'expenses.json'
    assert json.loads(file.read_text(encoding='utf-8')) == [{'name':'车票','cents':300}]
    file.write_text('invalid JSON', encoding='utf-8')
    bad = run([str(exe)], cwd, env, '1\n午餐\n1800\n0\n')
    assert '读取 expenses.json 失败' in bad.stdout and file.read_text(encoding='utf-8') == 'invalid JSON'
    print('PROJECT_OK', flush=True)

def main():
    compiler, env = swift_environment()
    probe = run([compiler, '--version'], ROOT, env)
    if probe.returncode and os.name == 'nt':
        # The toolchain frontend still works when the Windows driver cannot start.
        compiler = str(pathlib.Path(compiler).with_name('swift-frontend.exe'))
        probe = run([compiler, '-version'], ROOT, env)
    if probe.returncode:
        raise RuntimeError(probe.stderr)
    version = probe.stdout.strip()
    course = json.loads((ROOT/'public/course.json').read_text(encoding='utf-8'))
    scenes = [dict(scene, chapterKey=ch['key']) for ch in course['chapters'] for scene in ch['scenes']]
    # An ASCII build root works with Windows linker tools that expect local-codepage paths.
    build_root = pathlib.Path(os.environ.get('PUBLIC') or pathlib.Path.home().parent/'Public') if os.name == 'nt' else None
    with tempfile.TemporaryDirectory(prefix='swift-course-', dir=build_root) as directory:
        temp = pathlib.Path(directory)
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            futures = [(s["key"],pool.submit(verify_scene,s,temp,compiler,env)) for s in scenes]
            report, failures = [], []
            for key, task in futures:
                try:
                    report.append(task.result())
                except Exception as error:
                    failures.append(f"{key}: {error}")
        if failures:
            raise RuntimeError('\n'.join(failures))
        verify_project(temp, compiler, env)
    (ROOT/'build/examples-verification.json').write_text(json.dumps(
        dict(swiftVersion=version, verified=report, interactiveProject=True),
        ensure_ascii=False, indent=2), encoding='utf-8')
    print('VERIFIED', len(report), version, flush=True)

if __name__ == '__main__':
    main()
