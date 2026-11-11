`timescale 1ns/1ps
module tb;
reg clk=0,rst=1,en=0; wire [3:0] count;
integer tests=0,errors=0;
counter4 dut(clk,rst,en,count);
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
@(posedge clk); #1; check(count===0);
@(negedge clk); rst=0; en=1; @(posedge clk); #1; check(count===4'd1);
@(negedge clk); rst=0; en=1; @(posedge clk); #1; check(count===4'd2);
@(negedge clk); rst=0; en=1; @(posedge clk); #1; check(count===4'd3);
@(negedge clk); rst=0; en=1; @(posedge clk); #1; check(count===4'd4);
@(negedge clk); rst=0; en=1; @(posedge clk); #1; check(count===4'd5);
@(negedge clk); rst=0; en=1; @(posedge clk); #1; check(count===4'd6);
@(negedge clk); rst=0; en=1; @(posedge clk); #1; check(count===4'd7);
@(negedge clk); rst=0; en=1; @(posedge clk); #1; check(count===4'd8);
@(negedge clk); rst=0; en=1; @(posedge clk); #1; check(count===4'd9);
@(negedge clk); rst=0; en=1; @(posedge clk); #1; check(count===4'd10);
@(negedge clk); rst=0; en=1; @(posedge clk); #1; check(count===4'd11);
@(negedge clk); rst=0; en=1; @(posedge clk); #1; check(count===4'd12);
@(negedge clk); rst=0; en=1; @(posedge clk); #1; check(count===4'd13);
@(negedge clk); rst=0; en=1; @(posedge clk); #1; check(count===4'd14);
@(negedge clk); rst=0; en=1; @(posedge clk); #1; check(count===4'd15);
@(negedge clk); rst=0; en=1; @(posedge clk); #1; check(count===4'd0);
@(negedge clk); rst=0; en=1; @(posedge clk); #1; check(count===4'd1);
@(negedge clk); rst=0; en=0; @(posedge clk); #1; check(count===4'd1);
@(negedge clk); rst=0; en=0; @(posedge clk); #1; check(count===4'd1);
@(negedge clk); rst=0; en=1; @(posedge clk); #1; check(count===4'd2);

 $display("CHECKS %0d ERRORS %0d",tests,errors);
 if(errors==0) $display("PASS");
 $finish;
end
endmodule
