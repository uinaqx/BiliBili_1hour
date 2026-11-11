# Verilog基础速查

使用Verilog-2005设计子集；测试平台与设计分开。

## 硬件描述与第一个电路

### 从输入到输出

视频起点：00:00:36

两个输入，一个输出；先说清规则

四种情况全部列出；两个都为一，输出才为一

### 模块的基本外形

视频起点：00:01:39

代码：and_gate.v

```verilog
module and_gate(input wire a, b, output wire y);
  assign y = a & b;
endmodule
```

module和endmodule围住电路；端口列出输入与输出

assign描述持续连接关系；分号不能遗漏

### 多个电路同时工作

视频起点：00:02:42

代码：parallel_gates.v

```verilog
module parallel_gates(input wire a, b,
  output wire y_and, y_or);
  assign y_and = a & b;
  assign y_or  = a | b;
endmodule
```

两条连续赋值描述两条支路；不是先算第一条再算第二条

同一输入可以送到多个电路；过程内部另有执行规则

### 仿真和综合

视频起点：00:03:44

仿真：给激励、看输出；测试平台负责检查

综合：转换为电路实现；仿真通过不等于已经上板

### 读懂第一份仿真结果

视频起点：00:04:50

编译成功与功能正确分开判断；四组输入覆盖一位与门

检查PASS与失败信息；命令和文件都在工程里

## 端口、信号与数值

### 端口与连接方向

视频起点：00:06:54

代码：mux2.v

```verilog
module mux2(input wire a, b, sel,
  output wire y);
  assign y = sel ? b : a;
endmodule
```

input进入模块，output离开模块；方向取决于端口声明

sel决定选择哪条数据；模块连接时先对接口

### wire与reg

视频起点：00:07:59

代码：mux_always.v

```verilog
module mux_always(input wire a, b, sel,
  output reg y);
  always @(*) begin
    if (sel) y = b;
    else     y = a;
  end
endmodule
```

wire常表示连接，reg可在过程内赋值；reg不等于一定产生寄存器

完整分支仍可描述组合逻辑；根据行为判断电路

### 位宽与进制

视频起点：00:09:07

4'b1010与4'hA都是四位1010；位宽、进制、比特值分开看

结果放不下会截断；常量尽量写明位宽

### 位选、片选与拼接

视频起点：00:10:11

代码：vector_demo.v

```verilog
module vector_demo(input wire [7:0] data,
  output wire [3:0] hi, lo,
  output wire [7:0] swapped);
  assign hi = data[7:4];
  assign lo = data[3:0];
  assign swapped = {lo, hi};
endmodule
```

data[7:4]与data[3:0]；先确认下标方向

{lo,hi}按顺序拼接；A5交换为5A

### 未知值与高阻态

视频起点：00:11:18

x：未知；z：高阻；先找来源再改代码

复位、连接、驱动都要检查；测试中的四态比较单独处理

## 运算符与连续赋值

### 按位、逻辑与归约

视频起点：00:13:19

代码：operators.v

```verilog
module operators(input wire [3:0] a, b,
  output wire [3:0] bit_and,
  output wire logic_and, parity);
  assign bit_and = a & b;
  assign logic_and = a && b;
  assign parity = ^a;
endmodule
```

a & b：逐位计算；0010 & 0001得到0000

a && b得到一位真值；^a是归约异或

### 加法与进位

视频起点：00:14:24

代码：adder.v

```verilog
module adder(input wire [3:0] a, b,
  output wire [3:0] low,
  output wire [4:0] full);
  assign low = a + b;
  assign full = {1'b0, a} + {1'b0, b};
endmodule
```

15+1的低四位为0000；四位计数器可能回绕

先零扩展，再做五位加法；明确保留进位

### 选择表达式

视频起点：00:15:28

代码：mux2.v

```verilog
module mux2(input wire a, b, sel,
  output wire y);
  assign y = sel ? b : a;
endmodule
```

sel ? b : a：真取b，假取a；先代入零和一检查

选中的输入变化才影响输出；测试不能只切换sel

### 移位与有符号数

视频起点：00:16:33

逻辑右移补零；算术右移结合有符号属性

1100无符号右移为0110；有符号算术右移可为1110

### 括号与比较

视频起点：00:17:41

用括号明确设计意图；长表达式可以拆中间信号

赋值与相等比较分开；结合上下文判断符号作用

## 组合过程与完整赋值

### 组合过程块

视频起点：00:19:43

代码：mux_always.v

```verilog
module mux_always(input wire a, b, sel,
  output reg y);
  always @(*) begin
    if (sel) y = b;
    else     y = a;
  end
endmodule
```

always @(*)描述组合过程；相关输入变化后重新计算

两个分支都给y赋值；组合过程中使用阻塞赋值

### 条件分支的完整性

视频起点：00:20:50

代码：mux_always.v

```verilog
module mux_always(input wire a, b, sel,
  output reg y);
  always @(*) begin
    if (sel) y = b;
    else     y = a;
  end
endmodule
```

写if时同时检查不成立的路径；每个输出都要逐一检查

else补齐另一种情况；默认值也必须符合功能要求

### case与默认分支

视频起点：00:21:52

代码：decoder.v

```verilog
module decoder(input wire [1:0] sel,
  output reg [3:0] y);
  always @(*) begin
    case (sel)
      2'b00: y = 4'b0001;
      2'b01: y = 4'b0010;
      2'b10: y = 4'b0100;
      default: y = 4'b1000;
    endcase
  end
endmodule
```

case把多个选择值分别处理；两位选择可对应四个输出位置

default要符合设计要求；不要用忽略未知位的写法掩盖问题

### 不完整赋值与锁存行为

视频起点：00:22:55

代码：latch_bad.v

```verilog
module latch_bad(input wire en, d,
  output reg q);
  always @(*) begin
    if (en) q = d;
  end
endmodule
```

反例：代码合法，但保留旧值；en=0时q不再跟随d

锁存行为与边沿触发不同；先确认是不是自己想要的电路

### 默认赋值的修正方法

视频起点：00:23:54

代码：latch_fixed.v

```verilog
module latch_fixed(input wire en, d,
  output reg q);
  always @(*) begin
    q = 1'b0;
    if (en) q = d;
  end
endmodule
```

先给默认值，再处理特定条件；默认值来自明确需求

后面的阻塞赋值可覆盖前值；语句顺序不等于物理延迟

## 时钟、触发器与计数器

### 时钟边沿与采样

视频起点：00:25:59

代码：dff.v

```verilog
module dff(input wire clk, rst, d,
  output reg q);
  always @(posedge clk) begin
    if (rst) q <= 1'b0;
    else     q <= d;
  end
endmodule
```

posedge表示从0到1的事件；不是整个高电平持续更新

边沿之间输入变，输出可保持；在上升沿采样当时的数据

### 同步复位

视频起点：00:27:06

代码：dff.v

```verilog
module dff(input wire clk, rst, d,
  output reg q);
  always @(posedge clk) begin
    if (rst) q <= 1'b0;
    else     q <= d;
  end
endmodule
```

复位建立明确初始状态；触发条件仍只有时钟上升沿

同步复位等到时钟边沿生效；测试要把复位放在边沿之间

### 异步复位的区别

视频起点：00:28:12

代码：async_dff.v

```verilog
module async_dff(input wire clk, rst, d,
  output reg q);
  always @(posedge clk or posedge rst) begin
    if (rst) q <= 1'b0;
    else     q <= d;
  end
endmodule
```

触发列表加入复位有效边沿；示例采用高有效异步复位

异步复位可以在时钟边沿之外生效；实际释放还需要时序设计

### 带使能的四位计数器

视频起点：00:29:15

代码：counter4.v

```verilog
module counter4(input wire clk, rst, en,
  output reg [3:0] count);
  always @(posedge clk) begin
    if (rst)      count <= 4'd0;
    else if (en)  count <= count + 4'd1;
  end
endmodule
```

复位优先，使能决定是否加一；时序块中可以有意保持旧值

使能不是另一个时钟；用统一时钟配合更新条件

### 回绕与观察时刻

视频起点：00:30:15

代码：counter4.v

```verilog
module counter4(input wire clk, rst, en,
  output reg [3:0] count);
  always @(posedge clk) begin
    if (rst)      count <= 4'd0;
    else if (en)  count <= count + 4'd1;
  end
endmodule
```

四位计数自然在15后回到0；指定终值要另外写条件

测试在边沿更新完成后观察；不要把测试延迟写进RTL

## 阻塞与非阻塞赋值

### 阻塞赋值的计算顺序

视频起点：00:32:16

代码：blocking_demo.v

```verilog
module blocking_demo(input wire clk, rst, d,
  output reg q1, q2);
  always @(posedge clk) begin
    if (rst) begin q1 = 0; q2 = 0; end
    else begin
      q1 = d;
      q2 = q1;
    end
  end
endmodule
```

同一过程内，=先更新再执行后句；后句可能读到刚写入的新值

组合计算可以使用阻塞赋值；时钟存储先明确逐拍关系

### 非阻塞赋值先读旧值

视频起点：00:33:21

代码：pipeline.v

```verilog
module pipeline(input wire clk, rst, d,
  output reg q1, q2);
  always @(posedge clk) begin
    if (rst) begin q1 <= 0; q2 <= 0; end
    else begin
      q1 <= d;
      q2 <= q1;
    end
  end
endmodule
```

<=先计算右边，再安排更新；本拍q2读取旧q1

第一次采到1：q1=1，q2=0；下一拍再向后传递

### 用逐拍表推导输出

视频起点：00:34:24

代码：pipeline.v

```verilog
module pipeline(input wire clk, rst, d,
  output reg q1, q2);
  always @(posedge clk) begin
    if (rst) begin q1 <= 0; q2 <= 0; end
    else begin
      q1 <= d;
      q2 <= q1;
    end
  end
endmodule
```

先列旧值，再列新值；算q2时不能偷用新q1

不跳变也可能已经执行更新；逐个边沿核对采样值

### 过程之间与驱动来源

视频起点：00:35:29

不要依赖源文件上下顺序安排过程；明确每个信号的驱动者

同一状态的复位与更新统一描述；避免随意多过程驱动同一寄存器

### 测试平台避开采样冲突

视频起点：00:36:30

下降沿驱动，上升沿采样；更新完成后再检查

仿真观察安排不是硬件延迟模型；驱动、采样、检查分清楚

## 层次化、参数与重复结构

### 实例化与命名连接

视频起点：00:38:34

代码：hierarchy.v

```verilog
module hierarchy(input wire a, b, sel,
  output wire y);
  wire selected;
  mux2 u_mux(.a(a), .b(b), .sel(sel),
             .y(selected));
  assign y = ~selected;
endmodule
```

模块名表示类型，实例名表示具体实例；推荐命名端口连接

先核对端口，再沿内部线追踪；实例化表示硬件层次

### 参数决定结构宽度

视频起点：00:39:41

代码：reg_param.v

```verilog
module reg_param #(parameter WIDTH = 4)(
  input wire clk, rst,
  input wire [WIDTH-1:0] d,
  output reg [WIDTH-1:0] q);
  always @(posedge clk) begin
    if (rst) q <= {WIDTH{1'b0}};
    else     q <= d;
  end
endmodule
```

parameter在展开结构时确定；WIDTH决定端口位数

同一模块生成不同宽度实例；重复拼接让所有位归零

### generate与重复电路

视频起点：00:40:51

代码：generate_inv.v

```verilog
module generate_inv #(parameter WIDTH = 4)(
  input wire [WIDTH-1:0] a,
  output wire [WIDTH-1:0] y);
  genvar i;
  generate
    for (i=0; i<WIDTH; i=i+1) begin: bits
      assign y[i] = ~a[i];
    end
  endgenerate
endmodule
```

generate在展开时复制结构；四个位同时有取反关系

循环不自动消耗时钟周期；分拍完成需要明确控制状态

### 函数组织组合计算

视频起点：00:41:56

代码：parity_fn.v

```verilog
module parity_fn(input wire [3:0] a,
  output wire y);
  function parity4;
    input [3:0] value;
    begin parity4 = ^value; end
  endfunction
  assign y = parity4(a);
endmodule
```

function组织一段组合计算；传统写法给函数名赋返回值

本课组合函数不含时间等待；仍需验证具体功能

### 文件、顶层与编译范围

视频起点：00:43:04

顶层是本次展开的入口；文件名、模块名、实例名分开

先检查缺文件和拼写；设计RTL与测试平台分目录

## 有限状态机

### 先画状态与转移

视频起点：00:45:05

状态记录当前处于哪个阶段；先画转移规则再写代码

两位可以编码三个状态；还要考虑未使用的编码

### 保存当前状态

视频起点：00:46:10

代码：fsm.v · 节选

```verilog
module fsm(input wire clk, rst, go, done,
  output wire busy, output reg [1:0] state);
  localparam IDLE=2'd0, RUN=2'd1, WAIT=2'd2;
  reg [1:0] next_state;
  always @(posedge clk) begin
    if (rst) state <= IDLE;
    else     state <= next_state;
  end
```

localparam给状态编码命名；state与next_state分开

时钟过程保存当前状态；复位优先进入空闲

### 计算下一状态

视频起点：00:47:13

代码：fsm.v · 节选

```verilog
  always @(*) begin
    next_state = state;
    case (state)
      IDLE: if (go) next_state = RUN;
      RUN:  if (done) next_state = WAIT;
      WAIT: next_state = IDLE;
      default: next_state = IDLE;
    endcase
  end
```

next_state先默认保持；然后按当前状态处理条件

default安排未列出编码的去向；状态图与条件逐项对应

### 输出与当前状态

视频起点：00:48:21

代码：fsm.v · 节选

```verilog
    case (state)
      IDLE: if (go) next_state = RUN;
      RUN:  if (done) next_state = WAIT;
      WAIT: next_state = IDLE;
      default: next_state = IDLE;
    endcase
  end
  assign busy = (state == RUN);
endmodule
```

busy由当前state决定；RUN时为1，其余为0

分别追踪状态、计划与输出；不要只凭状态机名称猜波形

### 逐拍验证转移条件

视频起点：00:49:25

既测转移，也测不满足条件时保持；每次跳转都对应明确条件

当前输入假设同一时钟环境；上板还需要处理外部信号

## 测试平台、波形与排错

### 测试平台的角色

视频起点：00:51:30

代码：tb_and_gate.v · 节选

```verilog
`timescale 1ns/1ps
module tb;
reg a,b,sel; wire y;
integer tests=0,errors=0;
and_gate dut(.a(a),.b(b),.y(y));
```

测试平台提供激励和观察；设计与测试承担不同角色

dut连接实际被测设计；每个检查点都应有明确预期

### initial与测试延迟

视频起点：00:52:37

代码：tb_and_gate.v · 节选

```verilog
initial begin
 $dumpfile("wave.vcd"); $dumpvars(0,tb);
a=0; b=0; sel=0; #4; check(y===1'b0);
a=0; b=1; sel=0; #4; check(y===1'b0);
a=1; b=0; sel=0; #4; check(y===1'b0);
a=1; b=1; sel=0; #4; check(y===1'b1);
 $display("CHECKS %0d ERRORS %0d",tests,errors);
 if(errors==0) $display("PASS");
 $finish;
end
endmodule
```

initial安排一次测试过程；时间等待属于测试环境

显示结果与结束仿真都要安排；PASS来自明确的测试检查

### 自动检查与四态比较

视频起点：00:53:38

代码：tb_and_gate.v · 节选

```verilog
task check;
 input condition;
 begin
 tests=tests+1;
 if(condition!==1'b1) begin
 errors=errors+1; $display("FAIL time=%0t",$time);
 end
 end
endtask
```

未知结果也不能算通过；记录失败时刻帮助定位

预期来自独立需求模型；还要确认测试能发现故意错误

### 从波形定位问题

视频起点：00:54:44

先选关键的时钟、控制和状态；横轴是仿真时间

从最早分歧点向前追；波形与自动检查互相补充

### 区分三类失败

视频起点：00:55:49

先区分编译失败和功能失败；运行成功也可能漏测

修正后重跑相同刺激；通过结论受检查范围限制

## 综合小设计与学习路线

### 把需求拆成更新规则

视频起点：00:57:59

先明确复位、使能和终值规则；保存计数与一位灯状态

仿真参数小，方便看清变化；上板参数要结合实际时钟

### 终值计数与翻转

视频起点：00:59:04

代码：blink.v

```verilog
module blink #(parameter LIMIT = 3)(
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
endmodule
```

检查旧count是否达到LIMIT-1；达到后清零并翻转led

统一时钟配合使能；计数宽度限制参数范围

### 验证保持与再次启动

视频起点：01:00:09

代码：blink.v

```verilog
module blink #(parameter LIMIT = 3)(
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
endmodule
```

时钟继续走，禁用时状态保持；恢复后从保留状态继续

覆盖复位、终值、暂停与恢复；预期按需求独立计算

### 从RTL仿真到真实硬件

视频起点：01:01:14

上板还需器件、引脚和时钟约束；仿真不替代实现与时序检查

外部输入要处理抖动与同步；参数与位宽随需求核对

### 读代码与排错的固定顺序

视频起点：01:02:22

接口→位宽→驱动→触发→更新；用小刺激推导并验证

从小电路逐步组合；每次改动都配对应检查
