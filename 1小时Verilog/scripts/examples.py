"""Independent reference arithmetic; simulator stimuli are in examples/catalog.py."""
def wrap4(value):return value%16
def parity(value):return bin(value).count('1')%2
def blink_after_enabled_edges(n,limit=3):return n%limit,(n//limit)%2
