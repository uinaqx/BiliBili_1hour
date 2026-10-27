"""Networking teaching diagrams. Authored semantic phases, motion persists at its endpoint.

Canvas is exactly 1165x310 because draw.py pastes it into the lesson board at (78,603).
Graphics live left of x=780; the right strip x=805..1150 is reserved for annotations.
"""
import functools, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import examples

BG = '#10243a'; TEXT = '#eff5ff'; BLUE = '#70cfff'; ORANGE = '#ffbd68'
GREEN = '#8fe0b2'; RED = '#ff929c'; GRID = '#33506a'; MUTED = '#a2b7cc'
DATA = examples.all_examples(); BOXES = []


@functools.lru_cache(32)
def font(size): return ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', size)


def txt(d, xy, value, size=25, color=TEXT, anchor='lt'):
    d.text(tuple(xy), str(value), font=font(size), fill=color, anchor=anchor)


def wrap(d, value, xy, width=330, size=24, color=TEXT):
    x, y = xy; row = ''
    for ch in str(value):
        if row and font(size).getlength(row + ch) > width:
            txt(d, (x, y), row, size, color); y += 34; row = ''
        row += ch
    if row:
        txt(d, (x, y), row, size, color); y += 34
    return y


def note(d, a, b=''):
    y = wrap(d, a, (805, 46), 335, 24, ORANGE) + 18
    if b:
        y = wrap(d, b, (805, y), 335, 22, MUTED)
    assert y < 300, ('Diagram annotation overflow', a, b)


def line(d, a, b, color=GRID, width=3):
    a = np.asarray(a, float); b = np.asarray(b, float); v = b - a
    visible = [(0., 1.)]
    for x, y, xx, yy in BOXES:
        enter, leave = 0., 1.; hit = True
        for axis, low, high in [(0, x + 2, xx - 2), (1, y + 2, yy - 2)]:
            if abs(v[axis]) < 1e-9:
                if not low <= a[axis] <= high:
                    hit = False; break
            else:
                p, q = sorted([(low - a[axis]) / v[axis], (high - a[axis]) / v[axis]])
                enter = max(enter, p); leave = min(leave, q)
        if not hit or enter >= leave:
            continue
        pieces = []
        for low, high in visible:
            if high <= enter or low >= leave:
                pieces.append((low, high)); continue
            if low < enter: pieces.append((low, enter))
            if high > leave: pieces.append((leave, high))
        visible = pieces
    for low, high in visible:
        if high - low > 1e-8:
            d.line([tuple(a + v * low), tuple(a + v * high)], fill=color, width=width)


def path(d, points, color=GRID, width=3):
    for a, b in zip(points, points[1:]): line(d, a, b, color, width)


def dot(d, p, color=ORANGE, r=6):
    d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=color)


def arrow(d, a, b, color=GRID, width=3):
    a = np.array(a, float); b = np.array(b, float); v = b - a; n = np.linalg.norm(v)
    if n < 2: return
    line(d, a, b, color, width); v /= n; q = np.array([-v[1], v[0]])
    d.polygon([tuple(b), tuple(b - v * 11 + q * 5), tuple(b - v * 11 - q * 5)], fill=color)


def box(d, rect, label, color=BLUE, fill='#18374b', size=23):
    x, y, xx, yy = rect; BOXES.append(rect)
    d.rounded_rectangle(rect, 8, fill=fill, outline=color, width=2)
    lines = str(label).split('\n'); height = len(lines) * int(size * 1.32)
    for i, s in enumerate(lines):
        assert font(size).getlength(s) < xx - x - 6, ('Box text overflow', label, rect)
        txt(d, ((x + xx) / 2, (y + yy - height) / 2 + int(size * 0.66) + i * int(size * 1.32)), s, size, color, 'mm')


def packet(d, points, t, color=ORANGE):
    lengths = [float(np.linalg.norm(np.array(b) - a)) for a, b in zip(points, points[1:])]
    amount = max(0, min(1, t)) * sum(lengths); p = np.array(points[-1], float)
    for a, b, length in zip(points, points[1:], lengths):
        if amount <= length + 1e-7:
            p = np.array(a) + (np.array(b) - a) * min(1, amount / max(length, 1e-9)); break
        amount -= length
    dot(d, p, color)


def bar(d, x, y, value, total, color=ORANGE, width=520, height=12, bg='#1d4152'):
    d.rounded_rectangle((x, y, x + width, y + height), 4, fill=bg)
    d.rounded_rectangle((x, y, x + max(3, round(width * value / total)), y + height), 4, fill=color)


def stage(t, index, total=1):
    """0 until progress passes the indexed step, then 1."""
    return 1.0 if t * total >= index else 0.0


# ------------------------------------------------------------------ 1 delay
def delay(d, phase, t):
    if phase == 'send':
        box(d, (20, 55, 170, 135), '主机A')
        box(d, (620, 55, 770, 135), '主机B')
        txt(d, (395, 32), '1 Mbps 链路', 24, MUTED, 'mm')
        txt(d, (395, 152), '1000字节 = 8000比特', 24, ORANGE, 'mm')
        arrow(d, (170, 95), (620, 95), GRID, 3)
        for i in range(8):
            x = 195 + i * 52; color = GREEN if i / 8 <= t else '#2c4a5e'
            d.rounded_rectangle((x, 82, x + 34, 108), 5, fill=color, outline=GRID)
        txt(d, (395, 180), '已推出 ' + str(min(8, int(t * 8))) + ' / 8 个毫秒', 23, GREEN, 'mm')
        note(d, '发送时延 = 数据量 ÷ 带宽', '8000bit ÷ 1Mbps = 8ms；与距离无关')
    else:
        txt(d, (560, 20), '2000 km 光纤链路', 24, MUTED, 'mm')
        arrow(d, (120, 120), (740, 120), GRID, 3)
        for km in [0, 500, 1000, 1500, 2000]:
            x = 120 + 620 * km / 2000
            line(d, (x, 112), (x, 128), MUTED, 2)
            txt(d, (x, 134), str(km) + 'km', 19, MUTED, 'mt')
        dot(d, (120 + 620 * t, 120), ORANGE, 8)
        txt(d, (430, 210), '传播速度 2×10^8 m/s', 23, GREEN, 'mm')
        note(d, '传播时延 = 距离 ÷ 传播速度', '2000km ÷ 2×10^8m/s = 10ms；与带宽无关')
    txt(d, (20, 275), '时延构成：发送 + 传播 + 处理 + 排队', 22, TEXT)


# ------------------------------------------------------------------ 2 stack
def stack(d, phase, t):
    layers = DATA['stack']['layers']
    for i, layer in enumerate(layers):
        y = 18 + i * 52
        box(d, (40, y, 340, y + 44), layer['name'] + ' · ' + layer['pdu'])
    if phase == 'encap':
        arrow(d, (380, 40), (380, 265), BLUE, 3)
        yy = 40 + (265 - 40) * t
        dot(d, (380, yy), ORANGE, 9)
        for i, layer in enumerate(layers[1:], 1):
            header = layer.get('header')
            if not header: continue
            at = (i - 0.5) / 4
            if t >= at * 0.9:
                txt(d, (395, 18 + i * 52 + 8), '+ ' + header['label'] + ' ' + str(header['bytes']) + 'B', 21, GREEN)
        note(d, '封装：每下一层加一个首部', '链路层还有帧尾 FCS 4字节')
    else:
        arrow(d, (720, 265), (720, 40), GREEN, 3)
        yy = 265 - (265 - 40) * t
        dot(d, (720, yy), ORANGE, 9)
        for i, layer in enumerate(layers[1:], 1):
            header = layer.get('header')
            if not header: continue
            if t >= 0.15 * (4 - i + 1):
                txt(d, (395, 18 + i * 52 + 8), '- ' + header['label'], 21, RED)
        note(d, '解封装：接收方逐层去掉首部', '每层只把本层首部去掉后交给上层')
    txt(d, (40, 282), '首部合计 ' + str(DATA['stack']['total_header_bytes']) + ' 字节（TCP20+IP20+帧14+FCS4）', 21, MUTED)


# ------------------------------------------------------------------ 3 signal
def signal(d, phase, t):
    bits = DATA['signal']['bits']; x0 = 30; cell = 42; y = 95
    if phase == 'code':
        for i, bit in enumerate(bits):
            x = x0 + i * cell; lit = (i + 1) / len(bits) <= t + 1e-9
            txt(d, (x + cell / 2, 40), str(bit), 25, TEXT if lit else '#3a5a70', 'mm')
            d.rectangle((x, 62, x + cell - 2, 86), outline=GRID, fill='#162c40')
            if lit:
                # Manchester: high-then-low for 1, low-then-high for 0
                half = (cell - 2) / 2
                if bit == 1:
                    d.rectangle((x + 1, 64, x + 1 + half, 74), fill=GREEN); d.rectangle((x + 1 + half, 74, x + cell - 1, 84), fill=BLUE)
                else:
                    d.rectangle((x + 1, 74, x + 1 + half, 84), fill=BLUE); d.rectangle((x + 1 + half, 64, x + cell - 1, 74), fill=GREEN)
        txt(d, (30, 118), '曼彻斯特编码：每个码元中间跳变一次，接收方可提取时钟', 22, MUTED)
        txt(d, (30, 160), '比特率 = 波特率 × 每码元比特数', 23, ORANGE)
        txt(d, (30, 196), '这里每码元 1 比特，所以 2000 波特 = 2000 bps', 22, TEXT)
        note(d, '编码解决“比特怎么变成电平”', '数字数据用离散电平表示')
    else:
        symbol_bits = DATA['signal']['bits_per_symbol']
        levels = DATA['signal']['symbol_levels']
        txt(d, (30, 30), '每 ' + str(symbol_bits) + ' 比特组成一个码元，共 16 种状态', 24, ORANGE)
        for i, level in enumerate(levels[:4]):
            x = 30 + i * 180; lit = (i + 1) / 4 <= t + 1e-9
            d.rounded_rectangle((x, 70, x + 160, 150), 8, fill='#162c40', outline=GREEN if lit else GRID, width=2)
            txt(d, (x + 80, 94), '码元 ' + str(i + 1), 22, TEXT, 'mm')
            txt(d, (x + 80, 126), '电平 ' + str(level), 24, GREEN if lit else MUTED, 'mm')
            # level meter grows as the narration walks through the symbols
            grow = max(0.0, min(1.0, t * 4 - i))
            d.rectangle((x + 128, 140 - round(58 * grow), x + 150, 142), fill=ORANGE if grow else '#24384a')
        txt(d, (30, 170), '波特率 2000 码元/秒 × 4 比特 = 8000 bps', 24, GREEN)
        txt(d, (30, 206), '比特率与波特率不是同一个量，看清题目给的是哪个', 22, MUTED)
        note(d, '一个码元可以携带多个比特', '16种状态 → log2(16)=4 比特')


# ------------------------------------------------------------------ 4 frame
def frame(d, phase, t):
    fields = [('目的MAC', 6, 90), ('源MAC', 6, 90), ('类型', 2, 60), ('数据 46~1500B', 1500, 300), ('FCS', 4, 70)]
    active = min(len(fields) - 1, int(t * len(fields) + 1e-9))
    x = 25; y = 70
    for i, (label, size, width) in enumerate(fields):
        fill = '#1d4152'
        if phase == 'field' and i == active: fill = '#2f4d63'
        if phase == 'send' and label == 'FCS': fill = '#3b2f1a'
        d.rounded_rectangle((x, y, x + width, y + 62), 6, fill=fill, outline=ORANGE if (phase == 'field' and i == active) else BLUE, width=3 if (phase == 'field' and i == active) else 2)
        txt(d, (x + width / 2, y + 18), label, 19, TEXT, 'mm')
        txt(d, (x + width / 2, y + 44), str(size) + 'B', 20, ORANGE, 'mm')
        x += width + 4
    txt(d, (25, 150), '最小帧 64B（数据不足 46B 要填充），最大 1518B', 22, MUTED)
    if phase == 'field':
        txt(d, (25, 30), '以太网帧：首部 14 字节 + 数据 + 帧尾 4 字节', 24, ORANGE)
        note(d, '目的6+源6+类型2+数据46~1500+FCS4', '类型字段标明上层协议，如 0x0800 是 IPv4')
    else:
        txt(d, (25, 30), '发送：交换机按帧转发，FCS 用于检错', 24, ORANGE)
        box(d, (25, 190, 175, 255), '主机A')
        box(d, (610, 190, 770, 255), '交换机端口')
        packet(d, [(175, 222), (610, 222)], t)
        txt(d, (390, 268), '帧在链路上传输，MAC 地址逐段有效', 21, GREEN, 'mm')
        note(d, '小于 64B 的残帧视为冲突碎片丢弃', 'FCS 用 CRC 检查比特错误，不纠错')


# ------------------------------------------------------------------ 5 switch
def switch(d, phase, t):
    box(d, (300, 70, 540, 210), '交换机', GREEN)
    ports = [(300, 95), (300, 140), (300, 185), (540, 140)]
    for i, (x, y) in enumerate(ports, 1):
        fill = '#' + ('3b2f1a' if (phase == 'learn' and i == 1) or (phase == 'forward' and i == 4) else '162c40')
        d.rectangle((x - 14, y - 10, x + 14, y + 10), fill=fill, outline=ORANGE)
        if x < 400:
            txt(d, (x - 22, y - 10), '口' + str(i), 18, MUTED, 'rt')
        else:
            txt(d, (x + 22, y - 10), '口' + str(i), 18, MUTED)
    for i, (label, y) in enumerate([('H1', 80), ('H2', 125), ('H3', 170)]):
        box(d, (20, y, 150, y + 40), label, BLUE, size=21)
        arrow(d, (150, y + 20), (286, 95 + i * 45), GRID, 2)
    box(d, (690, 200, 790, 245), 'H5', BLUE, size=21)
    arrow(d, (554, 140), (690, 222), GRID, 2)
    table = [('H1', '1'), ('H2', '2'), ('H3', '3')]
    txt(d, (20, 250), 'MAC表：' + '  '.join(a + '→口' + b for a, b in table), 21, MUTED)
    if phase == 'learn':
        packet(d, [(150, 100), (300, 95)], t)
        txt(d, (20, 20), '学习：收到帧时，把源 MAC 和入端口记进表里', 23, ORANGE)
        note(d, '源 MAC 用来学习', '目的 MAC 用来决定转发端口')
    else:
        packet(d, [(540, 140), (690, 222)], t)
        txt(d, (20, 20), '转发：按目的 MAC 查表，只从对应端口发出', 23, ORANGE)
        note(d, '查不到目的 MAC 时从其他端口泛洪', '每端口一个冲突域，整台交换机一个广播域')


# ------------------------------------------------------------------ 6 subnet
def subnet(d, phase, t):
    table = DATA['subnet']['table']
    if phase == 'mask':
        base_bits = DATA['subnet']['base_bits']; x0 = 30; cell = 21
        txt(d, (30, 20), '192.168.1.0/24 的地址位（前 24 位是网络位）', 23, ORANGE)
        shown = min(32, int(t * 32 + 1e-9))
        for i, bit in enumerate(base_bits):
            x = x0 + i * cell
            lit = i < shown
            network = i < 24
            d.rectangle((x, 58, x + cell - 2, 96), fill=('#1b3d4f' if network else '#3a2f1d') if lit else '#16293a', outline=(BLUE if network else ORANGE) if lit else GRID)
            if lit: txt(d, (x + (cell - 2) / 2, 66), bit, 17, TEXT, 'mt')
        line(d, (x0 + 24 * cell - 2, 48), (x0 + 24 * cell - 2, 116), ORANGE, 3)
        txt(d, (x0 + 24 * cell + 4, 118), '/24 边界', 20, ORANGE)
        line(d, (x0 + 26 * cell - 2, 48), (x0 + 26 * cell - 2, 150), GREEN, 3)
        txt(d, (x0 + 26 * cell + 4, 148), '/26 边界', 20, GREEN)
        txt(d, (30, 176), '新掩码 255.255.255.192：网络位 26 位，主机位 6 位', 23, TEXT)
        txt(d, (30, 212), '块大小 = 2^6 = 64 个地址', 24, GREEN)
        note(d, '掩码与 IP 按位与得到网络地址', '主机位全 0 网络地址，全 1 广播地址')
    else:
        txt(d, (30, 18), '把 192.168.1.0/24 等分为 4 个 /26 子网（第三段为可用范围末位）', 22, ORANGE)
        for i, row in enumerate(table):
            x = 24 + i * 187; width = 170
            selected = i == 1
            grow = max(0.0, min(1.0, t * 4 - i))
            if grow <= 0:
                d.rounded_rectangle((x, 52, x + width, 214), 8, fill='#12222f', outline=GRID, width=1)
                txt(d, (x + width / 2, 128), '待分配', 18, MUTED, 'mm')
                continue
            d.rounded_rectangle((x, 52, x + width, 214), 8, fill='#1d4152' if selected else '#162c40', outline=GREEN if selected else GRID, width=2)
            txt(d, (x + width / 2, 58), '子网 ' + str(row['index']), 20, GREEN if selected else MUTED, 'mt')
            if grow < 0.6:
                continue
            color = TEXT if selected else MUTED
            txt(d, (x + 8, 92), '网络 ' + row['network'].rsplit('.', 1)[1].rjust(3), 18, color)
            txt(d, (x + 8, 124), '广播 ' + row['broadcast'].rsplit('.', 1)[1], 18, color)
            txt(d, (x + 8, 156), '可用 ' + row['first'].rsplit('.', 1)[1] + '~' + row['last'].rsplit('.', 1)[1], 18, color)
            txt(d, (x + 8, 188), '共 ' + str(row['hosts']) + ' 个主机', 17, color)
        txt(d, (30, 236), '每个子网 64 个地址（192.168.1.x），可用主机 62 个', 21, TEXT)
        note(d, '子网2：网络 192.168.1.64，广播 .127', '可用地址 .65 到 .126；块大小 64')


# ------------------------------------------------------------------ 7 ipheader
def ipheader(d, phase, t):
    if phase == 'field':
        row1 = [('版本', 4), ('首部长度', 4), ('服务类型', 8), ('总长度', 16), ('标识', 16), ('标志', 3), ('片偏移', 13)]
        row2 = [('TTL', 8), ('协议', 8), ('校验和', 16), ('源IP地址', 32), ('目的IP地址', 32)]
        scale = 700 / 160
        active = min(11, int(t * 12 + 1e-9))
        x = 25
        for i, (label, bits) in enumerate(row1):
            w = bits * scale
            color = ORANGE if i == active else BLUE
            d.rounded_rectangle((x, 46, x + w - 2, 100), 4, fill='#2f4d63' if i == active else '#1b3d4f', outline=color, width=3 if i == active else 2)
            if w > 34: txt(d, (x + w / 2, 58), label, 16, TEXT, 'mt')
            x += w
        x = 25
        for j, (label, bits) in enumerate(row2):
            w = bits * scale; index = len(row1) + j
            color = ORANGE if index == active else BLUE
            d.rounded_rectangle((x, 112, x + w - 2, 166), 4, fill='#2f4d63' if index == active else '#1b3d4f', outline=color, width=3 if index == active else 2)
            if w > 34: txt(d, (x + w / 2, 124), label, 16, TEXT, 'mt')
            x += w
        txt(d, (25, 178), '固定首部 20 字节（160 位），选项另计', 22, MUTED)
        txt(d, (25, 214), '分片相关：标识、标志(MF/DF)、片偏移', 23, ORANGE)
        note(d, '首部长度以 4 字节为单位', '片偏移以 8 字节为单位')
    else:
        frag = DATA['ipheader']['fragments']
        txt(d, (30, 18), '4000 字节数据报（首部20B + 数据3980B）走 MTU=1500 链路', 22, ORANGE)
        total = DATA['ipheader']['total_bytes']; scale = 700 / total; x = 25
        for i, f in enumerate(frag):
            keep = 1.0 if t * 3 >= i + 0.45 else max(0.0, t * 3 - i)
            w = f['total'] * scale
            d.rounded_rectangle((x, 70, x + max(3, round(w * keep)) - 3, 130), 5, fill='#1b3d4f', outline=GREEN)
            if keep > 0.55:
                txt(d, (x + w / 2, 82), '片' + str(f['index']), 20, GREEN, 'mt')
                txt(d, (x + w / 2, 108), str(f['total']) + 'B', 18, TEXT, 'mt')
                txt(d, (x + w / 2, 140), '偏移' + str(f['offset']), 18, ORANGE, 'mt')
                txt(d, (x + w / 2, 164), 'MF=' + str(f['mf']), 18, ORANGE, 'mt')
            x += w + 3
        txt(d, (25, 200), '数据长度 1480 + 1480 + 1020 = 3980 字节', 22, TEXT)
        txt(d, (25, 232), '除最后一片外，每片数据长度必须是 8 的倍数', 22, GREEN)
        note(d, '片偏移 = 该片首个数据字节 ÷ 8', '偏移 0、185、370 对应 0、1480、2960')


# ------------------------------------------------------------------ 8 nat
def nat(d, phase, t):
    box(d, (12, 92, 212, 198), '内网主机\n192.168.1.10:3000', BLUE, size=18)
    box(d, (330, 80, 560, 215), '', GREEN, size=20)
    txt(d, (330, 50), 'NAT 路由器', 23, GREEN)
    txt(d, (445, 80), '转换表', 19, ORANGE, 'mt')
    table = [('内', '192.168.1.10:3000'), ('外', '202.1.1.1:40000'), ('协议', 'TCP')]
    for i, (label, value) in enumerate(table):
        y = 116 + i * 30
        txt(d, (350, y), label, 18, MUTED)
        txt(d, (392, y), value, 18, TEXT)
    box(d, (650, 92, 800, 198), '公网\n202.1.1.1:40000', ORANGE, size=18)
    if phase == 'out':
        arrows = [(212, 145), (330, 145)]
        packet(d, arrows, t)
        arrow(d, (560, 145), (650, 145), ORANGE, 3)
        txt(d, (262, 105), '源端口3000', 19, ORANGE, 'mt')
        txt(d, (605, 160), '源改为', 18, ORANGE, 'mt')
        note(d, '出去：把源地址和源端口改成公网映射', '私有地址不能被公网直接路由')
    else:
        arrow(d, (650, 145), (560, 145), ORANGE, 3)
        packet(d, [(560, 145), (330, 145), (212, 145)], t)
        txt(d, (605, 105), '目的40000', 19, ORANGE, 'mt')
        txt(d, (262, 160), '还原为3000', 18, ORANGE, 'mt')
        note(d, '回来：按转换表把目的地址和端口改回内网', '一台 NAT 可让多台内网主机共用公网 IP')
    txt(d, (20, 240), 'NAT 改的是 IP 首部里的地址和端口字段', 22, MUTED)


# ------------------------------------------------------------------ 9 route
def route(d, phase, t):
    entries = DATA['route']['entries']
    txt(d, (25, 16), '路由表（目的网络 / 前缀 / 下一跳）', 23, ORANGE)
    for i, e in enumerate(entries):
        y = 48 + i * 34
        active = (phase == 'lookup' and t > (i + 1) / (len(entries) + 1)) or (phase == 'forward' and e['next_hop'] == DATA['route']['expected'])
        fill = '#1d4152' if active else '#162c40'
        d.rounded_rectangle((25, y, 560, y + 30), 5, fill=fill, outline=GREEN if active else GRID)
        txt(d, (35, y + 5), e['dest'], 19, TEXT)
        txt(d, (250, y + 5), '前缀' + str(e['prefix']), 19, MUTED)
        txt(d, (370, y + 5), e['next_hop'], 19, GREEN if active else MUTED)
    txt(d, (25, 194), '目的 IP：' + DATA['route']['query'], 23, BLUE)
    if phase == 'lookup':
        txt(d, (25, 228), '逐条与掩码按位与，结果等于表项网络才算匹配', 21, TEXT)
        note(d, '先看哪些表项匹配目的地址', '再用最长前缀排除较粗的匹配')
    else:
        arrow(d, (300, 194), (300, 214), GREEN, 3)
        txt(d, (25, 228), '多条匹配时取前缀最长的一条：' + str(DATA['route']['expected_prefix']) + ' 位 → ' + DATA['route']['expected'], 21, GREEN)
        note(d, '最长前缀匹配：' + DATA['route']['query'], '→ 192.168.1.64/27，下一跳 ' + DATA['route']['expected'])
    box(d, (620, 150, 780, 208), '下一跳路由器\n' + DATA['route']['expected'], GREEN, size=20)
    packet(d, [(560, 175), (650, 179)], t if phase == 'forward' else 0)


# ------------------------------------------------------------------ 10 handshake
def handshake(d, phase, t):
    xs, xc = 250, 620
    txt(d, (xs, 16), '客户端', 24, BLUE, 'mt'); txt(d, (xc, 16), '服务器', 24, GREEN, 'mt')
    line(d, (xs, 42), (xs, 268), MUTED, 2); line(d, (xc, 42), (xc, 268), MUTED, 2)
    msgs = DATA['handshake']['phases'][phase]['messages']
    step = min(52, 210 / max(1, len(msgs)))
    for i, msg in enumerate(msgs):
        y = 58 + i * step
        left_to_right = msg['direction'] == 'c2s'
        x1, x2 = (xs, xc) if left_to_right else (xc, xs)
        color = BLUE if left_to_right else GREEN
        local = max(0.0, min(1.0, t * len(msgs) - i))
        head = x1 + (x2 - x1) * local
        if local > 0.02:
            arrow(d, (x1, y), (head, y), color, 3)
            dot(d, (head, y), ORANGE, 5)
        label = msg['kind']
        if 'seq' in msg: label += ' seq=' + str(msg['seq'])
        if 'ack' in msg: label += ' ack=' + str(msg['ack'])
        if local > 0.45:
            txt(d, ((x1 + x2) / 2, y - 24), label, 20, ORANGE, 'mt')
        if local >= 1:
            txt(d, (x2 + 6 if left_to_right else x2 - 6, y + 6), '收到', 17, GREEN, 'rt' if not left_to_right else 'lt')
    state = DATA['handshake']['phases'][phase]['state']
    txt(d, (20, 282), state, 21, TEXT)
    hint = {'syn': ('三次握手的第 1、2 步', '确认双方收发能力与初始序号'),
            'established': ('第 3 步 ACK 后连接建立', 'SYN 和 FIN 都会消耗一个序号'),
            'fin': ('四次挥手：两个方向分别关闭', '收到 FIN 只表示对方没有数据要发了'),
            'timewait': ('主动关闭方等待 2MSL', '保证最后的 ACK 能到达并让旧报文消散')}[phase]
    note(d, hint[0], hint[1])


# ------------------------------------------------------------------ 11 window
def window(d, phase, t):
    x0, width = 40, 700; seq_max = 7000; scale = width / seq_max
    txt(d, (25, 8), '发送方视角：MSS = 1000 字节，发送窗口 = 4000 字节', 22, ORANGE)
    if phase == 'send':
        slided = 0.0
    else:
        slided = max(0.0, min(1.0, (t - 0.15) / 0.35))
    lo = round(1 + 2000 * slided); hi = lo + 3999
    a = x0 + (lo - 1) * scale; b = x0 + hi * scale
    d.rounded_rectangle((a, 40, b, 58), 5, fill='#20404f', outline=BLUE, width=2)
    txt(d, ((a + b) / 2, 44), '窗口 [' + str(lo) + ', ' + str(hi) + ']', 18, BLUE, 'mt')
    line(d, (x0, 80), (x0 + width, 80), MUTED, 2)
    for k in range(0, 8):
        x = x0 + k * 1000 * scale
        line(d, (x, 74), (x, 86), MUTED, 2)
        txt(d, (x, 88), str(k * 1000 if k else 1), 17, MUTED, 'mt')
    for i, seq in enumerate(DATA['window']['sent']):
        if phase == 'send' and t * 4 < i:
            continue
        x = x0 + (seq - 1) * scale
        acked = seq + 1000 <= DATA['window']['ack']
        fill = '#2f5a45' if acked else '#4a3a1f'
        d.rounded_rectangle((x, 124, x + 1000 * scale - 4, 158), 4, fill=fill, outline=GREEN if not acked else MUTED)
        txt(d, (x + 46, 130), str(seq), 17, TEXT, 'mt')
    if phase == 'send':
        txt(d, (25, 176), '窗口内已发出 4 段，但都还没有被确认', 22, TEXT)
        txt(d, (25, 208), '已用窗口 4000B，暂时不能再发新数据', 22, MUTED)
        note(d, '窗口限制未确认数据的最大量', '发送窗口 = min(cwnd, rwnd)')
    else:
        if t > 0.3:
            xack = x0 + 2001 * scale
            arrow(d, (xack, 176), (xack, 84), GREEN, 3)
            txt(d, (xack + 8, 108), 'ACK=2001', 19, GREEN)
        if t > 0.62:
            for seq in [4001, 5001]:
                x = x0 + (seq - 1) * scale
                d.rounded_rectangle((x, 124, x + 1000 * scale - 4, 158), 4, fill='#1d4152', outline=GREEN, width=2)
                txt(d, (x + 46, 130), str(seq), 17, GREEN, 'mt')
        txt(d, (25, 176), '确认 2001 后窗口左移，变为 [2001, 6000]', 22, GREEN)
        txt(d, (25, 208), '空出的 2000B 可以新发 4001 与 5001 两段', 22, TEXT)
        note(d, '确认号表示“期望收到的下一个字节”', '窗口左边界随确认前移')


# ------------------------------------------------------------------ 12 congestion
def congestion(d, phase, t):
    left, right, top, bottom = 70, 720, 40, 250
    xmax, ymax = 16, 24
    line(d, (left, bottom), (right, bottom), MUTED, 2)
    line(d, (left, bottom), (left, top), MUTED, 2)
    for k in range(0, 5):
        y = bottom - (bottom - top) * k / 4
        txt(d, (left - 8, y - 8), str(int(ymax * k / 4)), 17, MUTED, 'rt')
    for k in range(0, 17, 2):
        x = left + (right - left) * k / xmax
        txt(d, (x - 6, bottom + 8), str(k), 17, MUTED, 'mt')
    txt(d, (left - 54, top - 26), 'cwnd', 20, ORANGE)
    txt(d, (right - 30, bottom + 30), '轮次', 20, ORANGE)

    def pt(rnd, cwnd):
        return (left + (right - left) * rnd / xmax, bottom - (bottom - top) * cwnd / ymax)

    if phase == 'slow':
        points = [(0, 1), (1, 2), (2, 4), (3, 8), (4, 16), (5, 17), (6, 18), (7, 19), (8, 20)]
        line(d, pt(0, 16), pt(xmax, 16), ORANGE, 2)
        txt(d, (pt(0, 16)[0] + 6, pt(0, 16)[1] - 26), 'ssthresh = 16', 19, ORANGE)
        reveal = max(1, int(round(t * (len(points) - 1))))
        shown = points[:reveal + 1]
        for a, b in zip(shown, shown[1:]): line(d, pt(*a), pt(*b), GREEN, 4)
        for rnd, cwnd in shown:
            dot(d, pt(rnd, cwnd), GREEN, 5)
        for rnd, cwnd in shown:
            txt(d, (pt(rnd, cwnd)[0], pt(rnd, cwnd)[1] - 20), str(cwnd), 17, GREEN, 'mt')
        note(d, '慢启动：每轮翻倍 1→2→4→8→16', '到 ssthresh 后转拥塞避免，每轮加 1')
    else:
        rise = [(0, 1), (1, 2), (2, 4), (3, 8), (4, 16), (5, 17), (6, 18), (7, 19), (8, 20), (9, 21), (10, 22), (11, 23), (12, 24)]
        shown = max(2, min(len(rise), int(t * (len(rise) + 4)) + 1))
        for a, b in zip(rise[:shown - 1], rise[1:shown]): line(d, pt(*a), pt(*b), GREEN, 3)
        if shown >= len(rise):
            dot(d, pt(12, 24), RED, 7)
            txt(d, (pt(12, 24)[0] - 6, pt(12, 24)[1] - 22), '超时', 19, RED, 'rt')
        if t > 0.62:
            line(d, pt(0, 12), pt(xmax, 12), ORANGE, 2)
            txt(d, (pt(0, 12)[0] + 6, pt(0, 12)[1] + 6), '新 ssthresh = 12', 19, ORANGE)
        if t > 0.72:
            restart = [(12, 1), (13, 2), (14, 4), (15, 8)]
            steps = max(1, int((t - 0.72) / 0.28 * len(restart)) + 1)
            for a, b in zip(restart[:steps - 1], restart[1:steps]): line(d, pt(*a), pt(*b), BLUE, 4)
            dot(d, pt(12, 1), BLUE, 6)
        note(d, '超时：ssthresh 减半为 12，cwnd 回到 1', '再慢启动 1→2→4→8→12，然后拥塞避免')


# ------------------------------------------------------------------ 13 dnsflow
def dnsflow(d, phase, t):
    left, right, base = 40, 700, 250
    line(d, (left, base), (right, base), MUTED, 2)
    for ms in [0, 20, 40, 60]:
        x = left + (right - left) * ms / 60
        line(d, (x, base - 6), (x, base + 6), MUTED, 2)
        txt(d, (x, base + 10), str(ms) + 'ms', 18, MUTED, 'mt')
    txt(d, (left, base + 40), '首字节时间：0 → 60ms', 21, ORANGE)
    box(d, (30, 30, 170, 90), '浏览器', BLUE)
    box(d, (330, 30, 520, 90), 'DNS 服务器', GREEN)
    box(d, (330, 120, 520, 180), 'Web 服务器', ORANGE)
    arrow(d, (170, 105), (700, 105), GRID, 2)
    unit = (right - left) / 3.0
    if phase == 'dns':
        xa = left
        xb = left + unit
        arrow(d, (xa, 105), (xb, 105), BLUE, 3)
        txt(d, ((xa + xb) / 2, 88), 'DNS 查询 / 应答（1 RTT = 20ms）', 20, BLUE, 'mm')
        dot(d, (xa + (xb - xa) * t, 105), ORANGE, 7)
        note(d, '先把域名解析成 IP 地址', '本地缓存命中时这一步可以省掉')
    else:
        xhand = left + unit
        xhttp = left + 3 * unit
        arrow(d, (xhand, 105), (xhttp, 105), ORANGE, 3)
        txt(d, ((xhand + xhttp) / 2, 88), 'TCP 握手 + HTTP 请求响应（2 RTT = 40ms）', 19, ORANGE, 'mm')
        dot(d, (xhand + (xhttp - xhand) * t, 105), ORANGE, 7)
        note(d, '首字节 ≈ DNS + 握手 + 请求 = 3 RTT', '20ms × 3 = 60ms；HTTPS 还要加 TLS 握手')
    txt(d, (30, 220), '顺序：DNS 解析 → TCP 三次握手 → 发送 HTTP 请求', 22, TEXT)


# ------------------------------------------------------------------ dispatch
def render(visual, phase, t):
    BOXES.clear()
    im = Image.new('RGB', (1165, 310), BG); d = ImageDraw.Draw(im)
    kind = visual['kind']; t = max(0.0, min(1.0, float(t)))
    functions = dict(delay=delay, stack=stack, signal=signal, frame=frame, switch=switch,
                     subnet=subnet, ipheader=ipheader, nat=nat, route=route,
                     handshake=handshake, window=window, congestion=congestion, dnsflow=dnsflow)
    assert kind in functions, ('Unimplemented authored diagram', kind)
    assert phase in DATA['visuals'][kind], ('Unknown phase', kind, phase)
    functions[kind](d, phase, t)
    return im
