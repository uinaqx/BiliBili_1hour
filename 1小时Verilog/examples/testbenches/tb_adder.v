`timescale 1ns/1ps
module tb;
reg [3:0] a,b; wire [3:0] low; wire [4:0] full;
integer tests=0,errors=0;
adder dut(a,b,low,full);

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
a=1; b=2; #4; check(low===4'd3); check(full===5'd3);
a=7; b=8; #4; check(low===4'd15); check(full===5'd15);
a=15; b=1; #4; check(low===4'd0); check(full===5'd16);
a=15; b=15; #4; check(low===4'd14); check(full===5'd30);
 $display("CHECKS %0d ERRORS %0d",tests,errors);
 if(errors==0) $display("PASS");
 $finish;
end
endmodule
