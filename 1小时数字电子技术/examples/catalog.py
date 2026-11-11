"""Original synthesizable Verilog-2005 examples and independent simulation stimuli."""
DESIGNS={
'and_gate':'''module and_gate(input wire a, b, output wire y);
  assign y = a & b;
endmodule''',
'parallel_gates':'''module parallel_gates(input wire a, b,
  output wire y_and, y_or);
  assign y_and = a & b;
  assign y_or  = a | b;
endmodule''',
'mux2':'''module mux2(input wire a, b, sel,
  output wire y);
  assign y = sel ? b : a;
endmodule''',
'vector_demo':'''module vector_demo(input wire [7:0] data,
  output wire [3:0] hi, lo,
  output wire [7:0] swapped);
  assign hi = data[7:4];
  assign lo = data[3:0];
  assign swapped = {lo, hi};
endmodule''',
'operators':'''module operators(input wire [3:0] a, b,
  output wire [3:0] bit_and,
  output wire logic_and, parity);
  assign bit_and = a & b;
  assign logic_and = a && b;
  assign parity = ^a;
endmodule''',
'adder':'''module adder(input wire [3:0] a, b,
  output wire [3:0] low,
  output wire [4:0] full);
  assign low = a + b;
  assign full = {1'b0, a} + {1'b0, b};
endmodule''',
'mux_always':'''module mux_always(input wire a, b, sel,
  output reg y);
  always @(*) begin
    if (sel) y = b;
    else     y = a;
  end
endmodule''',
'decoder':'''module decoder(input wire [1:0] sel,
  output reg [3:0] y);
  always @(*) begin
    case (sel)
      2'b00: y = 4'b0001;
      2'b01: y = 4'b0010;
      2'b10: y = 4'b0100;
      default: y = 4'b1000;
    endcase
  end
endmodule''',
'latch_bad':'''module latch_bad(input wire en, d,
  output reg q);
  always @(*) begin
    if (en) q = d;
  end
endmodule''',
'latch_fixed':'''module latch_fixed(input wire en, d,
  output reg q);
  always @(*) begin
    q = 1'b0;
    if (en) q = d;
  end
endmodule''',
'dff':'''module dff(input wire clk, rst, d,
  output reg q);
  always @(posedge clk) begin
    if (rst) q <= 1'b0;
    else     q <= d;
  end
endmodule''',
'async_dff':'''module async_dff(input wire clk, rst, d,
  output reg q);
  always @(posedge clk or posedge rst) begin
    if (rst) q <= 1'b0;
    else     q <= d;
  end
endmodule''',
'counter4':'''module counter4(input wire clk, rst, en,
  output reg [3:0] count);
  always @(posedge clk) begin
    if (rst)      count <= 4'd0;
    else if (en)  count <= count + 4'd1;
  end
endmodule''',
'pipeline':'''module pipeline(input wire clk, rst, d,
  output reg q1, q2);
  always @(posedge clk) begin
    if (rst) begin q1 <= 0; q2 <= 0; end
    else begin
      q1 <= d;
      q2 <= q1;
    end
  end
endmodule''',
'blocking_demo':'''module blocking_demo(input wire clk, rst, d,
  output reg q1, q2);
  always @(posedge clk) begin
    if (rst) begin q1 = 0; q2 = 0; end
    else begin
      q1 = d;
      q2 = q1;
    end
  end
endmodule''',
'reg_param':'''module reg_param #(parameter WIDTH = 4)(
  input wire clk, rst,
  input wire [WIDTH-1:0] d,
  output reg [WIDTH-1:0] q);
  always @(posedge clk) begin
    if (rst) q <= {WIDTH{1'b0}};
    else     q <= d;
  end
endmodule''',
'generate_inv':'''module generate_inv #(parameter WIDTH = 4)(
  input wire [WIDTH-1:0] a,
  output wire [WIDTH-1:0] y);
  genvar i;
  generate
    for (i=0; i<WIDTH; i=i+1) begin: bits
      assign y[i] = ~a[i];
    end
  endgenerate
endmodule''',
'parity_fn':'''module parity_fn(input wire [3:0] a,
  output wire y);
  function parity4;
    input [3:0] value;
    begin parity4 = ^value; end
  endfunction
  assign y = parity4(a);
endmodule''',
'fsm':'''module fsm(input wire clk, rst, go, done,
  output wire busy, output reg [1:0] state);
  localparam IDLE=2'd0, RUN=2'd1, WAIT=2'd2;
  reg [1:0] next_state;
  always @(posedge clk) begin
    if (rst) state <= IDLE;
    else     state <= next_state;
  end
  always @(*) begin
    next_state = state;
    case (state)
      IDLE: if (go) next_state = RUN;
      RUN:  if (done) next_state = WAIT;
      WAIT: next_state = IDLE;
      default: next_state = IDLE;
    endcase
  end
  assign busy = (state == RUN);
endmodule''',
'blink':'''module blink #(parameter LIMIT = 3)(
  input wire clk, rst, en,
  output reg led, output reg [3:0] count);
  always @(posedge clk) begin
    if (rst) begin count <= 0; led <= 0; end
    else if (en) begin
      if (count == LIMIT-1) begin
        count <= 0;
        led <= ~led;
      end else count <= count + 1'b1;
    end
  end
endmodule''',
'hierarchy':'''module hierarchy(input wire a, b, sel,
  output wire y);
  wire selected;
  mux2 u_mux(.a(a), .b(b), .sel(sel),
             .y(selected));
  assign y = ~selected;
endmodule'''
}
TESTS=[]
def add(key,decl,inst,body,count,signals,dependencies=None):
 TESTS.append(dict(key=key,decl=decl,inst=inst,body=body,checks=count,signals=signals,dependencies=dependencies or [key]))

for key in ['and_gate','parallel_gates','mux2','mux_always','hierarchy']:
 outs='wire y_and, y_or;' if key=='parallel_gates' else 'wire y;'
 inst=f'{key} dut(.a(a),.b(b),'+('.y_and(y_and),.y_or(y_or)' if key=='parallel_gates' else ('.sel(sel),.y(y)' if key in ['mux2','mux_always','hierarchy'] else '.y(y)'))+');'
 lines=[];n=0
 for a in range(2):
  for b in range(2):
   for sel in (range(2) if key in ['mux2','mux_always','hierarchy'] else [0]):
    expected=(a&b) if key=='and_gate' else (b if sel else a)
    if key=='hierarchy':expected=1-expected
    lines.append(f"a={a}; b={b}; sel={sel}; #4; "+(f"check(y_and===1'b{a&b}); check(y_or===1'b{a|b});" if key=='parallel_gates' else f"check(y===1'b{expected});"));n+=2 if key=='parallel_gates' else 1
 add(key,'reg a,b,sel; '+outs,inst,'\n'.join(lines),n,['a','b','sel','y'] if key!='parallel_gates' else ['a','b','y_and','y_or'],['mux2','hierarchy'] if key=='hierarchy' else None)

add('vector_demo','reg [7:0] data; wire [3:0] hi,lo; wire [7:0] swapped;','vector_demo dut(data,hi,lo,swapped);','\n'.join(f"data=8'h{x:02x}; #4; check(hi===4'd{x>>4}); check(lo===4'd{x&15}); check(swapped===8'h{((x&15)<<4)|(x>>4):02x});" for x in [0,0xa5,0x3c,0xff]),12,['data','hi','lo','swapped'])
add('operators','reg [3:0] a,b; wire [3:0] bit_and; wire logic_and,parity;','operators dut(a,b,bit_and,logic_and,parity);','\n'.join(f"a=4'd{a}; b=4'd{b}; #4; check(bit_and===4'd{a&b}); check(logic_and===1'b{int(bool(a) and bool(b))}); check(parity===1'b{a.bit_count()%2});" for a,b in [(0,3),(2,1),(6,3),(15,10),(8,0)]),15,['a','b','bit_and','logic_and','parity'])
add('adder','reg [3:0] a,b; wire [3:0] low; wire [4:0] full;','adder dut(a,b,low,full);','\n'.join(f"a={a}; b={b}; #4; check(low===4'd{(a+b)%16}); check(full===5'd{a+b});" for a,b in [(1,2),(7,8),(15,1),(15,15)]),8,['a','b','low','full'])
add('decoder','reg [1:0] sel; wire [3:0] y;','decoder dut(sel,y);','\n'.join(f"sel=2'd{i}; #4; check(y===4'd{1<<i});" for i in range(4)),4,['sel','y'])
for key in ['latch_bad','latch_fixed']:
 add(key,'reg en,d; wire q;',f'{key} dut(en,d,q);',"en=1; d=0; #4; check(q===0); d=1; #4; check(q===1); en=0; d=0; #4; check(q==="+('1' if key=='latch_bad' else '0')+"); d=1; #4; check(q==="+('1' if key=='latch_bad' else '0')+");",4,['en','d','q'])
for key in ['dff','async_dff','counter4','pipeline','blocking_demo','reg_param','fsm','blink']:
 if key in ['dff','async_dff']:
  decl='reg clk=0,rst=1,d=0; wire q;';inst=f'{key} dut(clk,rst,d,q);';body="@(posedge clk); #1; check(q===0);\n";expected=0
  for d in [1,0,1,1,0,1]:body+=f"@(negedge clk); rst=0; d={d}; @(posedge clk); #1; check(q==={d});\n"
  body+="@(negedge clk); #2; rst=1; #1; check(q==="+('0' if key=='async_dff' else '1')+"); @(posedge clk); #1; check(q===0);";n=9;sig=['clk','rst','d','q']
 elif key=='counter4':
  decl='reg clk=0,rst=1,en=0; wire [3:0] count;';inst='counter4 dut(clk,rst,en,count);';body='@(posedge clk); #1; check(count===0);\n';value=0;n=1
  for en in [1]*17+[0,0,1]:
   if en:value=(value+1)%16
   body+=f"@(negedge clk); rst=0; en={en}; @(posedge clk); #1; check(count===4'd{value});\n";n+=1
  sig=['clk','en','count']
 elif key in ['pipeline','blocking_demo']:
  decl='reg clk=0,rst=1,d=0; wire q1,q2;';inst=f'{key} dut(clk,rst,d,q1,q2);';body='@(posedge clk); #1; check(q1===0 && q2===0);\n';old=0;n=1
  for d in [1,0,1,1,0,0]:
   body+=f"@(negedge clk); rst=0; d={d}; @(posedge clk); #1; check(q1==={d} && q2==={old if key=='pipeline' else d});\n";old=d;n+=1
  sig=['clk','d','q1','q2']
 elif key=='reg_param':
  decl='reg clk=0,rst=1; reg [7:0] d=0; wire [3:0] q4; wire [7:0] q8;';inst='reg_param #(.WIDTH(4)) u4(clk,rst,d[3:0],q4); reg_param #(.WIDTH(8)) u8(clk,rst,d,q8);';body='@(posedge clk); #1; check(q4===0 && q8===0);\n';n=1
  for x in [0xa5,0x3c,0xff,0]:body+=f"@(negedge clk); rst=0; d=8'h{x:02x}; @(posedge clk); #1; check(q4===4'd{x&15} && q8===8'd{x});\n";n+=1
  sig=['clk','d','q4','q8']
 elif key=='fsm':
  decl='reg clk=0,rst=1,go=0,done=0; wire busy; wire [1:0] state;';inst='fsm dut(clk,rst,go,done,busy,state);';body='@(posedge clk); #1; check(state===0 && busy===0);\n';n=1
  for go,done,state in [(0,0,0),(1,0,1),(0,0,1),(0,1,2),(0,0,0),(1,0,1),(0,1,2),(0,0,0)]:body+=f'@(negedge clk); rst=0; go={go}; done={done}; @(posedge clk); #1; check(state===2\'d{state} && busy==={int(state==1)});\n';n+=1
  sig=['clk','go','done','state','busy']
 else:
  decl='reg clk=0,rst=1,en=0; wire led; wire [3:0] count;';inst='blink #(.LIMIT(3)) dut(clk,rst,en,led,count);';body='@(posedge clk); #1; check(count===0 && led===0);\n';ticks=0;n=1
  for en in [1,1,1,0,0,1,1,1,1,1,1,1]:
   ticks+=en;body+=f"@(negedge clk); rst=0; en={en}; @(posedge clk); #1; check(count===4'd{ticks%3} && led==={ticks//3%2});\n";n+=1
  sig=['clk','en','count','led']
 add(key,decl,inst,body,n,sig)
for key in ['generate_inv','parity_fn']:
 add(key,'reg [3:0] a; '+('wire [3:0] y;' if key=='generate_inv' else 'wire y;'),f'{key} dut(a,y);','\n'.join(f"a=4'd{x}; #3; check(y==="+(f"4'd{15-x}" if key=='generate_inv' else f"1'b{x.bit_count()%2}")+");" for x in range(16)),16,['a','y'])

SPECIALS={
'four_state':'''module tb;
reg a; wire undriven; integer errors=0;
initial begin
  a=1'bx; #1;
  if ((a==1'b0)!==1'bx) errors=errors+1;
  if ((a===1'bx)!==1'b1) errors=errors+1;
  if (undriven!==1'bz) errors=errors+1;
  $display("a=%b undriven=%b ==0:%b ===x:%b",a,undriven,a==0,a===1'bx);
  $display("CHECKS 3 ERRORS %0d",errors);
  if (errors==0) $display("PASS"); $finish;
end
endmodule''',
'width_signed':'''module tb;
reg [3:0] narrow_value; reg signed [3:0] s;
reg [3:0] u; integer errors=0;
reg signed [3:0] arithmetic; reg [3:0] logical_shift;
initial begin
 narrow_value=4'b1111+4'b0001; s=4'b1100; u=4'b1100;
 arithmetic=s>>>1; logical_shift=u>>1; #1;
 if (narrow_value!==0) errors=errors+1;
 if (arithmetic!==4'b1110) errors=errors+1;
 if (logical_shift!==4'b0110) errors=errors+1;
 $display("narrow=%b arithmetic=%b logical=%b",narrow_value,arithmetic,logical_shift);
 $display("CHECKS 3 ERRORS %0d",errors);
 if(errors==0) $display("PASS"); $finish;
end
endmodule'''
}

def bench(t):
 clock='always #5 clk=~clk;' if 'clk' in t['decl'] else ''
 return '''`timescale 1ns/1ps
module tb;
'''+t['decl']+'\ninteger tests=0,errors=0;\n'+t['inst']+'\n'+clock+'''
task check;
 input condition;
 begin
 tests=tests+1;
 if(condition!==1'b1) begin
 errors=errors+1; $display("FAIL time=%0t",$time);
 end
 end
endtask
initial begin
 $dumpfile("wave.vcd"); $dumpvars(0,tb);
'''+t['body']+'''
 $display("CHECKS %0d ERRORS %0d",tests,errors);
 if(errors==0) $display("PASS");
 $finish;
end
endmodule
'''
