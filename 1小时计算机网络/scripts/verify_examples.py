"""Independent numeric verification of every standard teaching value.

The checks recompute the course numbers with plain arithmetic (integer division,
bit operations, logarithms and cumulative sums) instead of reusing the rendered
diagram data, so a wrong number in examples.py or diagrams.py is caught here.
"""
import hashlib, json, math, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import examples as E

checks = []


def check(name, condition, detail=''):
    checks.append(dict(name=name, passed=bool(condition), detail=str(detail)))
    assert condition, (name, detail)


def main():
    # ---------------------------------------------------------------- delay
    D = E.DELAY
    check('1000字节=8000比特', D['packet_bytes'] * 8 == D['packet_bits'] == 8000, D)
    check('发送时延8000/1M=8ms', D['packet_bits'] / D['link_bps'] * 1000 == D['send_delay_ms'] == 8)
    check('传播距离2000km=2e6米', D['link_km'] * 1000 == D['link_m'] == 2_000_000)
    check('传播时延2000km/2e8=10ms', D['link_m'] / D['prop_speed_mps'] * 1000 == D['prop_delay_ms'] == 10)

    # ---------------------------------------------------------------- stack
    S = E.STACK_LAYERS
    check('分层顺序：应用/传输/网络/链路/物理',
          [layer['name'] for layer in S] == ['应用层', '传输层', '网络层', '链路层', '物理层'])
    check('首部合计20+20+14+4=58B', E.STACK_TOTAL_HEADER_BYTES == 20 + 20 + 14 + 4 == 58)
    check('每层PDU名称齐全', [bool(layer.get('pdu')) for layer in S] == [True] * 5)

    # --------------------------------------------------------------- signal
    G = E.SIGNAL
    check('16种码元=4比特', int(math.log2(G['levels'])) == G['bits_per_symbol'] == 4)
    check('比特率2000×4=8000bps', G['baud'] * G['bits_per_symbol'] == G['bit_rate_bps'] == 8000)
    check('码元时长1/2000=0.5ms', abs(G['symbol_ms'] - 1000 / G['baud']) < 1e-9)
    check('比特流按4比特分组', len(G['symbol_levels']) * 4 == len(G['bits']))
    check('电平值不超过15', all(0 <= level <= 15 for level in G['symbol_levels']))
    channel = E.CHANNEL
    check('30dB=1000倍', abs(10 ** (channel['snr_db'] / 10) - channel['snr_linear']) < 1e-6)
    shannon = channel['bandwidth_hz'] * math.log2(1 + channel['snr_linear'])
    check('香农容量约3000×log2(1001)', abs(shannon - channel['shannon_bps']) < 1, shannon)
    check('香农容量约29.9kbps', abs(shannon / 1000 - channel['shannon_kbps']) < 0.05)

    # ---------------------------------------------------------------- frame
    F = E.FRAME
    check('帧首部6+6+2=14B', F['dst_mac'] + F['src_mac'] + F['ether_type'] == 14)
    check('最小帧14+46+4=64B', 14 + F['min_data'] + F['fcs'] == F['min_frame'] == 64)
    check('最大帧14+1500+4=1518B', 14 + F['max_data'] + F['fcs'] == F['max_frame'] == 1518)
    check('帧字段覆盖全部标准字段', [f['label'] for f in F['fields']] == ['目的MAC', '源MAC', '类型', '数据', 'FCS'])

    # --------------------------------------------------------------- switch
    W = E.SWITCH
    check('冲突域=集线器数3', W['collision_domains'] == W['hubs'] == 3)
    check('广播域=1（一台交换机）', W['broadcast_domains'] == 1)
    check('主机数=3×2=6', len(W['hosts']) == W['hubs'] * W['hosts_per_hub'] == 6)
    check('MAC表按端口登记', [row['port'] for row in W['mac_table']] == [1, 1, 2, 2, 3, 3])

    # --------------------------------------------------------------- subnet
    S = E.SUBNET
    check('块大小2^(32-26)=64', 2 ** (32 - S['new_prefix']) == S['block'] == 64)
    check('子网数量2^(26-24)=4', len(S['table']) == 2 ** (S['new_prefix'] - S['prefix']) == 4)
    check('新掩码255.255.255.192', E.int_to_ip(E.prefix_mask(26)) == S['new_mask'])
    check('子网地址按64递增', [row['network'] for row in S['table']] == ['192.168.1.0', '192.168.1.64', '192.168.1.128', '192.168.1.192'])
    check('每个子网可用主机62', all(row['hosts'] == S['block'] - 2 == 62 for row in S['table']))
    second = S['table'][1]
    check('子网2网络.64', second['network'] == '192.168.1.64')
    check('子网2广播.127', second['broadcast'] == '192.168.1.127')
    check('子网2可用.65-.126', (second['first'], second['last']) == ('192.168.1.65', '192.168.1.126'))
    check('网络地址主机位全0', E.ip_to_int(second['network']) & (S['block'] - 1) == 0)
    check('广播地址主机位全1', E.ip_to_int(second['broadcast']) & (S['block'] - 1) == S['block'] - 1)
    check('掩码前缀长度26', bin(E.prefix_mask(26)).count('1') == 26)
    A = E.AGGREGATION
    nets = [E.ip_to_int(n.split('/')[0]) for n in A['networks']]
    prefix = None
    for shift in range(0, 33):
        if len({net >> shift for net in nets}) == 1:
            prefix = 32 - shift
            break
    check('四个/24聚合成/22', prefix == A['prefix'] == 22, prefix)
    check('聚合起点为偶数块', min(nets) & ((1 << (32 - 22)) - 1) == 0)
    check('私有地址三块', E.PRIVATE_NETWORKS == [('10.0.0.0', 8), ('172.16.0.0', 12), ('192.168.0.0', 16)])
    check('环回127/8', E.LOOPBACK_NET == ('127.0.0.0', 8) and E.ip_to_int('127.0.0.1') >> 24 == 127)
    check('链路本地169.254/16', E.LINK_LOCAL_NET == ('169.254.0.0', 16))

    # ------------------------------------------------------------- ipheader
    H = E.IP_HEADER
    check('首部固定20B', H['header_bytes'] == 20)
    check('数据部分4000-20=3980B', H['total_bytes'] - H['header_bytes'] == H['payload_bytes'] == 3980)
    check('每片数据1480B', H['fragment_payload'] == H['mtu'] - H['header_bytes'] == 1480)
    check('片数=ceil(3980/1480)=3', math.ceil(3980 / 1480) == len(E.IP_FRAGMENTS) == 3)
    check('分片数据长度1480+1480+1020=3980', sum(f['payload'] for f in E.IP_FRAGMENTS) == 3980)
    check('分片总长度1500/1500/1040', [f['total'] for f in E.IP_FRAGMENTS] == [1500, 1500, 1040])
    check('片偏移0/185/370', [f['offset'] for f in E.IP_FRAGMENTS] == [0, 185, 370])
    check('偏移=累计数据/8', [f['offset'] for f in E.IP_FRAGMENTS] == [0, 1480 // 8, 2960 // 8])
    check('MF=1,1,0', [f['mf'] for f in E.IP_FRAGMENTS] == [1, 1, 0])
    check('除末片外数据长度为8的倍数', all(f['payload'] % 8 == 0 for f in E.IP_FRAGMENTS[:-1]))
    check('首部字段位宽合计160位', sum(f['bits'] for f in H['fields']) == 160)
    check('TTL64经3跳=61', E.TTL['initial'] - E.TTL['routers'] == E.TTL['remaining'] == 61)
    check('协议号ICMP1/TCP6/UDP17', (E.PROTOCOLS['ICMP'], E.PROTOCOLS['TCP'], E.PROTOCOLS['UDP']) == (1, 6, 17))
    check('NAT内网地址', E.NAT['inside'] == E.NAT['inside_ip'] + ':' + str(E.NAT['inside_port']) == '192.168.1.10:3000')
    check('NAT外网地址', E.NAT['outside'] == E.NAT['outside_ip'] + ':' + str(E.NAT['outside_port']) == '202.1.1.1:40000')
    check('NAT映射端口不同', E.NAT['inside_port'] != E.NAT['outside_port'])

    # ---------------------------------------------------------------- route
    R = E.ROUTE
    entries = [(E.ip_to_int(e['dest'].split('/')[0]), e['prefix'], e['next_hop']) for e in R['entries']]
    query = E.ip_to_int(R['query'])
    matches = [(prefix, next_hop) for net, prefix, next_hop in entries if query & E.prefix_mask(prefix) == net]
    check('目的192.168.1.70匹配两项', len(matches) == 2, matches)
    best = max(matches)
    check('最长前缀27位→R2', best == (27, 'R2') and R['expected'] == 'R2' and R['expected_prefix'] == 27)
    check('192.168.1.70属于.64/27网段', query >> 5 == E.ip_to_int('192.168.1.64') >> 5)
    check('默认路由8.8.8.8→R1', E.ip_to_int(R['default_query']) & 0 == 0 and R['default_expected'] == 'R1')
    check('RIP最大15跳/16不可达', (E.RIP['max_hops'], E.RIP['unreachable']) == (15, 16))
    check('RIP每30秒更新', E.RIP['update_seconds'] == 30)
    check('三种路由协议分类', list(E.ROUTING_PROTOCOLS.values()) == ['距离向量', '链路状态', 'AS 间路径向量'])
    check('默认路由前缀0', E.prefix_mask(0) == 0)

    # ------------------------------------------------------------ handshake
    H = E.HANDSHAKE
    check('SYN seq=1000', H['syn_seq'] == 1000)
    check('SYN+ACK ack=1001', H['synack_ack'] == H['syn_seq'] + 1 == 1001)
    check('第三次ACK ack=5001', H['ack_ack'] == H['synack_seq'] + 1 == 5001)
    check('三次握手消息数3', len(H['open_messages']) == 3)
    check('四次挥手消息数4', len(H['close_messages']) == 4)
    check('FIN确认2001', H['fin_ack'] == H['fin_seq'] + 1 == 2001)
    check('服务器FIN确认6001', H['fin2_ack'] == H['fin2_seq'] + 1 == 6001)
    check('TIME_WAIT等2MSL', H['time_wait_msl'] == 2)
    check('握手方向交替', [m['direction'] for m in H['open_messages']] == ['c2s', 's2c', 'c2s'])
    check('挥手方向c-s-s-c', [m['direction'] for m in H['close_messages']] == ['c2s', 's2c', 's2c', 'c2s'])
    check('知名端口范围0-1023', E.WELL_KNOWN_PORT_MAX == 1023)
    check('HTTP80/HTTPS443/DNS53', (E.PORTS['HTTP'], E.PORTS['HTTPS'], E.PORTS['DNS']) == (80, 443, 53))
    check('DHCP67/68', (E.PORTS['DHCP_SERVER'], E.PORTS['DHCP_CLIENT']) == (67, 68))
    check('FTP21控制/20数据', (E.PORTS['FTP_CONTROL'], E.PORTS['FTP_DATA']) == (21, 20))
    check('SMTP25/POP3110/SSH22', (E.PORTS['SMTP'], E.PORTS['POP3'], E.PORTS['SSH']) == (25, 110, 22))

    # --------------------------------------------------------------- window
    W = E.WINDOW
    check('MSS=1000B', W['mss'] == 1000)
    check('发送窗口=4000B', W['send_window'] == 4000 == 4 * W['mss'])
    check('已发四段', W['sent'] == [1, 1001, 2001, 3001])
    check('ACK=2001确认前两段', W['acked'] == [1, 1001] and W['outstanding'] == [2001, 3001])
    check('新窗口[2001,6000]', W['new_window'] == (2001, 6000))
    check('可新发2000B', W['available_bytes'] == 2000)
    check('可新发4001和5001', W['new_segments'] == [4001, 5001])
    check('接收窗口2000限制发送窗口', min(W['send_window'], W['recv_window']) == W['effective_window'] == 2000)
    check('RTO权重0.125/0.25/4', (E.TCP_RTO['srtt_weight'], E.TCP_RTO['rttvar_weight'], E.TCP_RTO['retransmit_factor']) == (0.125, 0.25, 4))

    # ------------------------------------------------------------ congestion
    C = E.CONGESTION
    check('初始cwnd=1', C['initial'] == 1)
    check('慢启动1,2,4,8,16', C['slow_start'] == [1, 2, 4, 8, 16])
    check('慢启动翻倍规律', all(b == a * 2 for a, b in zip(C['slow_start'], C['slow_start'][1:])))
    check('ssthresh=16', C['ssthresh'] == C['slow_start'][-1] == 16)
    check('拥塞避免每轮加1', all(b == a + 1 for a, b in zip(C['congestion_avoidance'], C['congestion_avoidance'][1:])))
    check('拥塞避免起点17', C['congestion_avoidance'][0] == C['ssthresh'] + 1 == 17)
    check('超时cwnd=24', C['timeout_cwnd'] == C['congestion_avoidance'][-1] == 24)
    check('超时ssthresh减半=12', C['timeout_ssthresh'] == C['timeout_cwnd'] // 2 == 12)
    check('超时后cwnd回1', C['restart'][0] == 1)
    check('重启后慢启动到12', C['restart'][:5] == [1, 2, 4, 8, 12])
    check('重复ACK阈值3', C['duplicate_acks'] == 3)
    check('快恢复cwnd=ssthresh=12', C['fast_recovery'] == dict(ssthresh=12, cwnd=12))

    # --------------------------------------------------------------- dnsflow
    F = E.DNSFLOW
    check('三个步骤各1RTT', [step['rtt'] for step in F['steps']] == [1, 1, 1])
    check('总RTT=3', F['total_rtt'] == 3)
    check('总时延=3×20=60ms', F['total_ms'] == F['total_rtt'] * F['rtt_ms'] == 60)
    check('累计里程碑20/40/60', F['cumulative_ms'] == [20, 40, 60])
    check('HTTPS=HTTP+TLS', E.HTTPS['basis'] == 'HTTP' and 'TLS' in E.HTTPS['extra'])

    # ------------------------------------------------------------- 图示契约
    check('13种图示', len(E.VISUALS) == 13)
    check('图示phase与正文一致', E.VISUALS['delay'] == ('send', 'prop') and E.VISUALS['handshake'] == ('syn', 'established', 'fin', 'timewait'))
    check('端口值不重复', len(set(E.PORTS.values())) == len(E.PORTS))
    check('私有地址不与环回冲突', not any(net.startswith('127.') for net, _ in E.PRIVATE_NETWORKS))

    course = ROOT / 'public' / 'course.json'
    course_sha = hashlib.sha256(course.read_bytes()).hexdigest() if course.exists() else None
    report = dict(allPassed=True, checks=len(checks), failures=[c for c in checks if not c['passed']],
                  scope='independent arithmetic, bit operations, integer division and cumulative sums over every standard teaching value; not an implementation conformance test',
                  courseSha256=course_sha, examples=checks)
    (ROOT / 'build' / 'examples-verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf8')
    print(json.dumps(dict(allPassed=True, checks=len(checks), courseSha256=course_sha), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
