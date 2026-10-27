"""Validate one chapter module before it is merged into the course build.
Usage: python scripts/validate_chapter.py chapters_b
Checks structure, narration length, notes, labels and diagram phases against docs/撰写规范.md.
"""
import importlib, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'content'))

CJK = re.compile(r'[\u4e00-\u9fff]')
VISUALS = {
    'stack': {'encap', 'decap'}, 'delay': {'send', 'prop'}, 'signal': {'code', 'sample'},
    'frame': {'field', 'send'}, 'switch': {'learn', 'forward'}, 'subnet': {'mask', 'split'},
    'ipheader': {'field', 'fragment'}, 'nat': {'out', 'back'}, 'route': {'lookup', 'forward'},
    'handshake': {'syn', 'established', 'fin', 'timewait'}, 'window': {'send', 'ack'}, 'congestion': {'slow', 'recover'},
    'dnsflow': {'dns', 'http'},
}
BAN = ['[', ']', '{', '}', '\\', '#', '*', '`', '<', '>', '|']
BOUNDS = dict(lesson=(225, 300), question=(95, 140), answer=(100, 155), overview=(130, 175))


def main(name):
    for stale in [m for m in sys.modules if m == 'author' or m.startswith('chapters_')]:
        del sys.modules[stale]
    mod = importlib.import_module(name)
    chapters = mod.CHAPTERS
    problems, report = [], []
    for ci, c in enumerate(chapters):
        pages = c['scenes']
        kinds = [s['kind'] for s in pages]
        is_first = name == 'chapters_a' and ci == 0
        if len(pages) != 8:
            problems.append(f"{c['key']} {c['title']}: 页面数 {len(pages)} != 8")
        if kinds.count('question') != 1:
            problems.append(f"{c['key']}: 需要且只需一道 question，实际 {kinds.count('question')}")
        if kinds.count('answer') != 1:
            problems.append(f"{c['key']}: 需要且只需一页 answer")
        if 'overview' in kinds and not is_first:
            problems.append(f"{c['key']}: overview 只允许出现在全课第 1 章")
        need = 5 if is_first else 6
        if kinds.count('lesson') != need:
            problems.append(f"{c['key']}: lesson 页应为 {need}，实际 {kinds.count('lesson')}")
        for s in pages:
            key = s['key']
            if not 4 <= len(s['title']) <= 24:
                problems.append(f'{key}: 标题长度 {len(s["title"])} 不在 4-24')
            if len(s['rows']) > 5:
                problems.append(f'{key}: rows 超过 5')
            if s.get('visual'):
                kind = s['visual']['kind']
                if kind not in VISUALS:
                    problems.append(f'{key}: 未知图示 {kind}')
                for p in s['parts']:
                    if p['phase'] not in VISUALS.get(kind, set()):
                        problems.append(f'{key}: 图示 {kind} 的 phase {p["phase"]} 不合法')
            for i, r in enumerate(s['rows'], 1):
                label = r['label']
                if len(label) > 20:
                    problems.append(f'{key} 行{i}: 行标签过长 {len(label)}')
                if r['math'] is None:
                    text = r['text']
                    if len(text) > 70:
                        problems.append(f'{key} 行{i}: 行文本过长 {len(text)}')
                    if len(text) < 6:
                        problems.append(f'{key} 行{i}: 行文本过短')
                combined = r['label'] + ('' if r['math'] else r['text'])
                for ch in BAN:
                    if ch in combined:
                        problems.append(f'{key} 行{i}: 含禁用字符 {ch!r}')
            total = 0
            for p in s['parts']:
                text = p['text']
                total += len(text)
                n = len(text)
                if not 100 <= n <= 155:
                    problems.append(f'{key} 段落{n}: 长度 {n} 不在 100-155')
                if n and text[-1] not in '。！？':
                    problems.append(f'{key}: 段落未以句末标点结束')
                if text.count('。') > 8:
                    problems.append(f'{key}: 句号过多 {text.count("。")}')
                if '？' in text or '！' in text:
                    problems.append(f'{key}: 旁白不要使用问号或感叹号（停顿只处理句号）')
                for ch in BAN:
                    if ch in text:
                        problems.append(f'{key}: 旁白含禁用字符 {ch!r}')
                if len(p['notes']) > 3:
                    problems.append(f'{key}: notes 超过 3 条')
                for note in p['notes']:
                    if len(note) > 30:
                        problems.append(f'{key}: note 过长 {len(note)}')
                if p['focus'] and max(p['focus']) > len(s['rows']):
                    problems.append(f'{key}: focus 超出 rows')
                if s.get('visual') and not p['moves']:
                    problems.append(f'{key}: 图示页缺少 anchor 动作')
                for mv in p['moves']:
                    if text.count(mv['anchor']) != 1:
                        problems.append(f'{key}: anchor 在段落中不唯一 {mv["anchor"]}')
            bounds = BOUNDS[s['kind']]
            if not bounds[0] <= total <= bounds[1]:
                problems.append(f'{key}: {s["kind"]}页旁白总量 {total} 不在 {bounds[0]}-{bounds[1]}')
        chapter_chars = sum(len(p['text']) for s in pages for p in s['parts'])
        low, high = (1680, 1850) if is_first else (1570, 1780)
        if not low <= chapter_chars <= high:
            problems.append(f"{c['key']}: 本章旁白总量 {chapter_chars} 不在 {low}-{high}")
        report.append(dict(key=c['key'], title=c['title'], pages=len(pages),
                           parts=sum(len(s['parts']) for s in pages), chars=chapter_chars,
                           minutes=round(chapter_chars / 4.883 / 60, 2),
                           cjk=len(CJK.findall(''.join(s['narration'] for s in pages))),
                           visuals=sum(1 for s in pages if s.get('visual'))))
    print(json.dumps(dict(module=name, chapters=report, problems=problems), ensure_ascii=False, indent=1))
    if problems:
        print(f'FAILED {len(problems)} problems', flush=True)
        sys.exit(1)
    print('CHAPTER_MODULE_OK', flush=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf8')
    if len(sys.argv) != 2:
        raise SystemExit('用法: python scripts/validate_chapter.py chapters_b')
    main(sys.argv[1])
