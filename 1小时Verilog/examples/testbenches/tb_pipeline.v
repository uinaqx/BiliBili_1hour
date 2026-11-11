`timescale 1ns/1ps
module tb;
reg clk=0,rst=1,d=0; wire q1,q2;
integer tests=0,errors=0;
pipeline dut(clk,rst,d,q1,q2);
always #5 clk=~clk;
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
@(posedge clk); #1; check(q1===0 && q2===0);
@(negedge clk); rst=0; d=1; @(posedge clk); #1; check(q1===1 && q2===0);
@(negedge clk); rst=0; d=0; @(posedge clk); #1; check(q1===0 && q2===1);
@(negedge clk); rst=0; d=1; @(posedge clk); #1; check(q1===1 && q2===0);
@(negedge clk); rst=0; d=1; @(posedge clk); #1; check(q1===1 && q2===1);
@(negedge clk); rst=0; d=0; @(posedge clk); #1; check(q1===0 && q2===1);
@(negedge clk); rst=0; d=0; @(posedge clk); #1; check(q1===0 && q2===0);

 $display("CHECKS %0d ERRORS %0d",tests,errors);
 if(errors==0) $display("PASS");
 $finish;
end
endmodule
