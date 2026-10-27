"""Deterministic teaching models for 《一小时学完计算机网络》.

This module is the single source of truth for every standard number that the
13 diagrams and the standalone verification script use.  The values are
transcribed from docs/撰写规范.md ("标准数值" section); diagrams.py only lays
them out on the 1165x310 canvas and verify_examples.py recomputes them with
independent arithmetic (bit operations, integer division, summation).
"""

# ------------------------------------------------------------------ 通用换算
BYTES_PER_KB = 1000
BITS_PER_BYTE = 8


def ip_to_int(address):
    """Dotted-quad IPv4 -> 32-bit integer (used to build the subnet table)."""
    parts = [int(part) for part in address.split('.')]
    assert len(parts) == 4 and all(0 <= part <= 255 for part in parts), address
    return (parts[0] << 24) | (parts[1] << 16) | (parts[2] << 8) | parts[3]


def int_to_ip(value):
    assert 0 <= value <= 0xFFFFFFFF, value
    return '.'.join(str((value >> shift) & 0xFF) for shift in (24, 16, 8, 0))


def prefix_mask(prefix):
    assert 0 <= prefix <= 32, prefix
    return (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF


# --------------------------------------------------- 第 2 章 发送时延与传播时延
DELAY = dict(
    packet_kb=1,
    packet_bytes=1 * BYTES_PER_KB,
    packet_bits=1 * BYTES_PER_KB * BITS_PER_BYTE,
    link_mbps=1,
    link_bps=1_000_000,
    send_delay_ms=8,
    link_km=2000,
    link_m=2_000_000,
    prop_speed_mps=200_000_000,
    prop_delay_ms=10,
)

# ------------------------------------------------------ 第 2 章 分层与封装
STACK_LAYERS = [
    dict(name='应用层', pdu='应用数据'),
    dict(name='传输层', pdu='TCP报文段', header=dict(label='TCP首部', bytes=20)),
    dict(name='网络层', pdu='IP数据报', header=dict(label='IP首部', bytes=20)),
    dict(name='链路层', pdu='以太网帧', header=dict(label='帧首部', bytes=14),
         trailer=dict(label='FCS', bytes=4)),
    dict(name='物理层', pdu='比特流'),
]
STACK_TOTAL_HEADER_BYTES = sum(
    (layer.get('header') or {}).get('bytes', 0) + (layer.get('trailer') or {}).get('bytes', 0)
    for layer in STACK_LAYERS
)

# ---------------------------------------------------- 第 2 章 编码、调制、信道
SIGNAL = dict(
    baud=2000,
    levels=16,
    bits_per_symbol=4,
    bit_rate_bps=8000,
    symbol_ms=0.5,
    bits=[1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1],
)


def symbol_levels(bits=None, bits_per_symbol=None):
    """Group the bit stream into symbols and return their decimal levels."""
    bits = SIGNAL['bits'] if bits is None else bits
    width = SIGNAL['bits_per_symbol'] if bits_per_symbol is None else bits_per_symbol
    assert len(bits) % width == 0, (len(bits), width)
    return [int(''.join(str(bit) for bit in bits[at:at + width]), 2)
            for at in range(0, len(bits), width)]


SIGNAL['symbol_levels'] = symbol_levels()

CHANNEL = dict(
    bandwidth_hz=3000,
    snr_db=30,
    snr_linear=1000,
    shannon_bps=29902,
    shannon_kbps=29.9,
)

# ------------------------------------------------------ 第 3 章 以太网帧结构
FRAME = dict(
    dst_mac=6,
    src_mac=6,
    ether_type=2,
    min_data=46,
    max_data=1500,
    fcs=4,
    min_frame=64,
    max_frame=1518,
    example=dict(dst='00:1A:2B:00:00:03', src='00:1A:2B:00:00:01', type='0x0800'),
)
FRAME['fields'] = [
    dict(label='目的MAC', size=dst, text=f'{dst}B')
    for dst in [FRAME['dst_mac']]
] + [
    dict(label='源MAC', size=FRAME['src_mac'], text=f"{FRAME['src_mac']}B"),
    dict(label='类型', size=FRAME['ether_type'], text=f"{FRAME['ether_type']}B"),
    dict(label='数据', size=FRAME['max_data'],
         text=f"{FRAME['min_data']}～{FRAME['max_data']}B"),
    dict(label='FCS', size=FRAME['fcs'], text=f"{FRAME['fcs']}B"),
]

# ------------------------------------------------ 第 3 章 交换机、冲突域与 MAC 表
SWITCH = dict(
    ports=4,
    hubs=3,
    hosts_per_hub=2,
    collision_domains=3,
    broadcast_domains=1,
)
SWITCH_HOSTS = [dict(name=f'H{i + 1}', hub=i // SWITCH['hosts_per_hub'] + 1,
                     port=i // SWITCH['hosts_per_hub'] + 1) for i in range(SWITCH['hubs'] * SWITCH['hosts_per_hub'])]
SWITCH_MAC_TABLE = [dict(host=host['name'], port=host['port']) for host in SWITCH_HOSTS]
SWITCH['hosts'] = SWITCH_HOSTS
SWITCH['mac_table'] = SWITCH_MAC_TABLE
SWITCH['forward_example'] = dict(src='H1', dst='H5', in_port=1, out_port=3)

# ------------------------------------------------ 第 4 章 子网掩码与子网划分
def subnet_table(base='192.168.1.0', prefix=24, new_prefix=26):
    """Split base/prefix into equal new_prefix subnets; return printable rows."""
    assert 0 <= prefix < new_prefix <= 32, (prefix, new_prefix)
    block = 2 ** (32 - new_prefix)
    count = 2 ** (new_prefix - prefix)
    first = ip_to_int(base)
    table = []
    for index in range(count):
        network = first + index * block
        table.append(dict(index=index + 1,
                          network=int_to_ip(network),
                          broadcast=int_to_ip(network + block - 1),
                          first=int_to_ip(network + 1),
                          last=int_to_ip(network + block - 2),
                          hosts=block - 2))
    return table


SUBNET = dict(
    base='192.168.1.0',
    prefix=24,
    base_mask='255.255.255.0',
    new_prefix=26,
    new_mask='255.255.255.192',
    block=64,
    hosts_per_subnet=62,
    index=2,
)
SUBNET['table'] = subnet_table(SUBNET['base'], SUBNET['prefix'], SUBNET['new_prefix'])
SUBNET['base_bits'] = format(ip_to_int(SUBNET['base']), '032b')
SUBNET['base_mask_bits'] = '1' * SUBNET['prefix'] + '0' * (32 - SUBNET['prefix'])
SUBNET['new_mask_bits'] = '1' * SUBNET['new_prefix'] + '0' * (32 - SUBNET['new_prefix'])


# ------------------------------- 第 4 章 CIDR 聚合与特殊地址（标准数值表）
AGGREGATION = dict(
    networks=['202.101.0.0/24', '202.101.1.0/24', '202.101.2.0/24', '202.101.3.0/24'],
    result='202.101.0.0/22',
    prefix=22,
)
PRIVATE_NETWORKS = [('10.0.0.0', 8), ('172.16.0.0', 12), ('192.168.0.0', 16)]
LOOPBACK_NET = ('127.0.0.0', 8)
LINK_LOCAL_NET = ('169.254.0.0', 16)

# ------------------------------------------- 第 5 章 IPv4 数据报与分片
IP_HEADER = dict(
    header_bytes=20,
    version=4,
    ihl=5,
    total_bytes=4000,
    payload_bytes=3980,
    mtu=1500,
    fragment_payload=1480,
)
IP_HEADER['fields'] = [
    dict(label='版本', bits=4),
    dict(label='首部长度', bits=4),
    dict(label='服务类型', bits=8),
    dict(label='总长度', bits=16),
    dict(label='标识', bits=16),
    dict(label='标志', bits=3),
    dict(label='片偏移', bits=13),
    dict(label='TTL', bits=8),
    dict(label='协议', bits=8),
    dict(label='首部校验和', bits=16),
    dict(label='源IP地址', bits=32),
    dict(label='目的IP地址', bits=32),
]
IP_FRAGMENTS = [
    dict(index=1, total=1500, payload=1480, offset=0, mf=1),
    dict(index=2, total=1500, payload=1480, offset=185, mf=1),
    dict(index=3, total=1040, payload=1020, offset=370, mf=0),
]
IP_HEADER['fragments'] = IP_FRAGMENTS

# ------------------------------------------------------- 第 5 章 NAT 地址转换
NAT = dict(
    inside_ip='192.168.1.10',
    inside_port=3000,
    outside_ip='202.1.1.1',
    outside_port=40000,
    inside='192.168.1.10:3000',
    outside='202.1.1.1:40000',
)

# ---------------------------------------------- 第 5 章 TTL 与协议号标准值
TTL = dict(initial=64, routers=3, remaining=61)
PROTOCOLS = dict(ICMP=1, TCP=6, UDP=17)
PORTS = dict(HTTP=80, HTTPS=443, DNS=53, DHCP_SERVER=67, DHCP_CLIENT=68,
             FTP_CONTROL=21, FTP_DATA=20, SMTP=25, POP3=110, SSH=22)
WELL_KNOWN_PORT_MAX = 1023

# ------------------------------------------------------ 第 6 章 最长前缀匹配
ROUTE = dict(
    entries=[
        dict(dest='0.0.0.0/0', prefix=0, next_hop='R1', kind='默认路由'),
        dict(dest='192.168.1.0/26', prefix=26, next_hop='直连', kind='直连'),
        dict(dest='192.168.1.64/27', prefix=27, next_hop='R2', kind='静态'),
        dict(dest='192.168.1.96/27', prefix=27, next_hop='R3', kind='静态'),
    ],
    query='192.168.1.70',
    expected='R2',
    expected_prefix=27,
    default_query='8.8.8.8',
    default_expected='R1',
)
RIP = dict(max_hops=15, unreachable=16, update_seconds=30)
ROUTING_PROTOCOLS = dict(RIP='距离向量', OSPF='链路状态', BGP='AS 间路径向量')

# ------------------------------------- 第 7 章 三次握手、四次挥手与 TCP 端口
HANDSHAKE = dict(
    syn_seq=1000,
    synack_seq=5000,
    synack_ack=1001,
    ack_ack=5001,
    fin_seq=2000,
    fin_ack=2001,
    fin2_seq=6000,
    fin2_ack=6001,
    time_wait_msl=2,
)
HANDSHAKE['open_messages'] = [
    dict(direction='c2s', kind='SYN', seq=HANDSHAKE['syn_seq']),
    dict(direction='s2c', kind='SYN+ACK', seq=HANDSHAKE['synack_seq'], ack=HANDSHAKE['synack_ack']),
    dict(direction='c2s', kind='ACK', ack=HANDSHAKE['ack_ack']),
]
HANDSHAKE['close_messages'] = [
    dict(direction='c2s', kind='FIN', seq=HANDSHAKE['fin_seq']),
    dict(direction='s2c', kind='ACK', ack=HANDSHAKE['fin_ack']),
    dict(direction='s2c', kind='FIN', seq=HANDSHAKE['fin2_seq']),
    dict(direction='c2s', kind='ACK', ack=HANDSHAKE['fin2_ack']),
]
HANDSHAKE['phases'] = {
    'syn': dict(messages=HANDSHAKE['open_messages'][:2],
                state='客户端已发 SYN，服务器回 SYN+ACK'),
    'established': dict(messages=HANDSHAKE['open_messages'],
                        state='三次握手完成，连接建立'),
    'fin': dict(messages=HANDSHAKE['close_messages'],
                state='双方各发一次 FIN，两个方向分别关闭'),
    'timewait': dict(messages=HANDSHAKE['close_messages'],
                     state='主动关闭方等待 2MSL 后进入关闭状态'),
}

# ------------------------------------------ 第 8 章 滑动窗口与 TCP 计时器
WINDOW = dict(
    mss=1000,
    send_window=4000,
    sent=[1, 1001, 2001, 3001],
    ack=2001,
    recv_window=2000,
)
WINDOW['acked'] = [seq for seq in WINDOW['sent'] if seq + WINDOW['mss'] <= WINDOW['ack']]
WINDOW['outstanding'] = [seq for seq in WINDOW['sent'] if seq + WINDOW['mss'] > WINDOW['ack']]
WINDOW['new_window'] = (WINDOW['ack'], WINDOW['ack'] + WINDOW['send_window'] - 1)
WINDOW['available_bytes'] = WINDOW['send_window'] - len(WINDOW['outstanding']) * WINDOW['mss']
WINDOW['new_segments'] = [WINDOW['ack'] + len(WINDOW['outstanding']) * WINDOW['mss'] + i * WINDOW['mss']
                          for i in range(WINDOW['available_bytes'] // WINDOW['mss'])]
WINDOW['effective_window'] = min(WINDOW['send_window'], WINDOW['recv_window'])
TCP_RTO = dict(srtt_weight=0.125, rttvar_weight=0.25, retransmit_factor=4)

# --------------------------------------------- 第 9 章 拥塞控制
CONGESTION = dict(
    initial=1,
    ssthresh=16,
    slow_start=[1, 2, 4, 8, 16],
    congestion_avoidance=[17, 18, 19, 20, 21, 22, 23, 24],
    timeout_cwnd=24,
    timeout_ssthresh=12,
    restart=[1, 2, 4, 8, 12, 13, 14, 15, 16],
    duplicate_acks=3,
)
CONGESTION['slow_sequence'] = list(enumerate(CONGESTION['slow_start'] + CONGESTION['congestion_avoidance']))
CONGESTION['recover_sequence'] = [(0, CONGESTION['timeout_cwnd'])] + [
    (index + 1, cwnd) for index, cwnd in enumerate(CONGESTION['restart'])]
CONGESTION['fast_recovery'] = dict(ssthresh=CONGESTION['timeout_cwnd'] // 2,
                                   cwnd=CONGESTION['timeout_cwnd'] // 2)

# ------------------------------------------ 第 10 章 DNS、HTTP 与访问网页
DNSFLOW = dict(
    rtt_ms=20,
    domain='www.example.com',
    steps=[
        dict(name='DNS 查询', rtt=1),
        dict(name='TCP 三次握手', rtt=1),
        dict(name='HTTP 请求响应', rtt=1),
    ],
)
DNSFLOW['total_rtt'] = sum(step['rtt'] for step in DNSFLOW['steps'])
DNSFLOW['total_ms'] = DNSFLOW['total_rtt'] * DNSFLOW['rtt_ms']
DNSFLOW['cumulative_ms'] = [DNSFLOW['rtt_ms'] * sum(step['rtt'] for step in DNSFLOW['steps'][:index + 1])
                            for index in range(len(DNSFLOW['steps']))]
HTTPS = dict(basis='HTTP', extra='TLS 握手与加密传输')

# --------------------------------------------------- 13 种图示及其合法 phase
VISUALS = {
    'delay': ('send', 'prop'),
    'stack': ('encap', 'decap'),
    'signal': ('code', 'sample'),
    'frame': ('field', 'send'),
    'switch': ('learn', 'forward'),
    'subnet': ('mask', 'split'),
    'ipheader': ('field', 'fragment'),
    'nat': ('out', 'back'),
    'route': ('lookup', 'forward'),
    'handshake': ('syn', 'established', 'fin', 'timewait'),
    'window': ('send', 'ack'),
    'congestion': ('slow', 'recover'),
    'dnsflow': ('dns', 'http'),
}


def all_examples():
    """Everything in one nested dict (diagrams.py consumes this via DATA)."""
    return dict(
        delay=DELAY,
        stack=dict(layers=STACK_LAYERS, total_header_bytes=STACK_TOTAL_HEADER_BYTES),
        signal=SIGNAL,
        channel=CHANNEL,
        frame=FRAME,
        switch=SWITCH,
        subnet=SUBNET,
        aggregation=AGGREGATION,
        ipheader=IP_HEADER,
        nat=NAT,
        ttl=TTL,
        protocols=PROTOCOLS,
        ports=PORTS,
        route=ROUTE,
        handshake=HANDSHAKE,
        window=WINDOW,
        congestion=CONGESTION,
        dnsflow=DNSFLOW,
        visuals=VISUALS,
    )
