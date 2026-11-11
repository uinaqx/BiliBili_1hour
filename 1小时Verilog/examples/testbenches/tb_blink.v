`timescale 1ns/1ps
module tb;
reg clk=0,rst=1,en=0; wire led; wire [3:0] count;
integer tests=0,errors=0;
blink #(.LIMIT(3)) dut(clk,rst,en,led,count);
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
@(posedge clk); #1; check(count===0 && led===0);
@(negedge clk); rst=0; en=1; @(posedge clk); #1; check(count===4'd1 && led===0);
@(negedge clk); rst=0; en=1; @(posedge clk); #1; check(count===4'd2 && led===0);
@(negedge clk); rst=0; en=1; @(posedge clk); #1; check(count===4'd0 && led===1);
@(negedge clk); rst=0; en=0; @(posedge clk); #1; check(count===4'd0 && led===1);
@(negedge clk); rst=0; en=0; @(posedge clk); #1; check(count===4'd0 && led===1);
@(negedge clk); rst=0; en=1; @(posedge clk); #1; check(count===4'd1 && led===1);
@(negedge clk); rst=0; en=1; @(posedge clk); #1; check(count===4'd2 && led===1);
@(negedge clk); rst=0; en=1; @(posedge clk); #1; check(count===4'd0 && led===0);
@(negedge clk); rst=0; en=1; @(posedge clk); #1; check(count===4'd1 && led===0);
@(negedge clk); rst=0; en=1; @(posedge clk); #1; check(count===4'd2 && led===0);
@(negedge clk); rst=0; en=1; @(posedge clk); #1; check(count===4'd0 && led===1);
@(negedge clk); rst=0; en=1; @(posedge clk); #1; check(count===4'd1 && led===1);

 $display("CHECKS %0d ERRORS %0d",tests,errors);
 if(errors==0) $display("PASS");
 $finish;
end
endmodule
