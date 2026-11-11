"""Executable lesson fragments and explicit test initial conditions, all CPU 8086."""
import json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
PRINT_U16="""print_u16:
push ax
push bx
push cx
push dx
xor cx, cx
mov bx, 10
.digits:
xor dx, dx
div bx
push dx
inc cx
test ax, ax
jnz .digits
.output:
pop dx
add dl, '0'
mov ah, 02h
int 21h
loop .output
pop dx
pop cx
pop bx
pop ax
ret
done: hlt
"""
DATA={'little_endian':{},'memory_rw':{0x200:bytes.fromhex('34 12 00 00')},'lea_address':{0x206:bytes.fromhex('78 56')},'byte_array_sum':{0x200:bytes([3,5,7])},'word_array_sum':{0x200:(100).to_bytes(2,'little')+(200).to_bytes(2,'little')+(300).to_bytes(2,'little')},'string_copy':{0x200:b'ABC'},'dos_string':{0x200:b'HI$'},'statistics':{0x200:bytes([3,5,7])}}
EXPECTED={
 'intro_add':{'ax':8},'register_parts':{'ax':0x1256},'little_endian':{'ax':0x1234,'bx':0x1234},'move_copy':{'ax':9,'bx':7},'memory_rw':{'ax':0x1234,'bx':0x200},'lea_address':{'dx':0x206,'ax':0x5678},'add_sub':{'ax':1},'carry_overflow':{'al':0x80},'inc_adc':{'ax':0,'dx':1},'multiply':{'ax':0xfff1},'division':{'al':33,'ah':10},'bit_mask':{'al':0x8a},'test_compare':{'al':0x81},'shifts':{'al':0x40,'bl':0xc0},'rotate':{'al':0xc0},'branch_equal':{'bx':1},'branch_unsigned':{'bx':1},'branch_signed':{'bx':1},'maximum_pair':{'ax':12,'bx':12},'flags_clobbered':{'bx':1,'dx':9},'count_loop':{'ax':6,'cx':0},'zero_loop_guard':{'ax':0,'cx':0},'byte_array_sum':{'ax':15,'si':0x203,'cx':0},'word_array_sum':{'ax':600,'si':0x206,'cx':0},'string_copy':{'si':0x203,'di':0x303,'cx':0},'push_pop':{'dx':0xabcd,'cx':0x1234,'sp':0x100},'near_call':{'ax':5,'bx':5,'sp':0xfffe},'save_register':{'ax':7,'bx':99,'sp':0xfffe},'stack_argument':{'ax':8,'sp':0xfffe},'ascii_digit':{'al':ord('5'),'bl':5},'dos_character':{},'dos_string':{},'dos_input':{'bl':7},'com_program':{'ds':0x1000,'sp':0xfffe},'machine_listing':{'ax':0x1235,'bx':0x1235},'flags_repaired':{'bx':1,'dx':0},'statistics':{'dx':15,'bl':7,'si':0x203,'cx':0},'statistics_output':{'sp':0xfffe}}
OUTPUT={'dos_character':'A','dos_string':'HI','dos_input':'7','com_program':'OK','statistics_output':'15 7'}
def catalog():
    course=json.loads((ROOT/'public/course.json').read_text(encoding='utf8'));runs={}
    for c in course['chapters']:
        for s in c['scenes']:
            if s.get('run'):
                key=s['run'];body='\n'.join(s['code']);assert key not in runs or runs[key]['body']==body
                runs[key]=dict(key=key,body=body,tail=PRINT_U16 if key=='statistics_output' else '' if key=='com_program' else '\nhlt\n',data=DATA.get(key,{}),expected=EXPECTED[key],input='7' if key=='dos_input' else '',output=OUTPUT.get(key,''))
    return runs
