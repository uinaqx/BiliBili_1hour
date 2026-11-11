`timescale 1ns/1ps
module tb;
reg clk=0,rst=1; reg [7:0] d=0; wire [3:0] q4; wire [7:0] q8;
integer tests=0,errors=0;
reg_param #(.WIDTH(4)) u4(clk,rst,d[3:0],q4); reg_param #(.WIDTH(8)) u8(clk,rst,d,q8);
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
@(posedge clk); #1; check(q4===0 && q8===0);
@(negedge clk); rst=0; d=8'ha5; @(posedge clk); #1; check(q4===4'd5 && q8===8'd165);
@(negedge clk); rst=0; d=8'h3c; @(posedge clk); #1; check(q4===4'd12 && q8===8'd60);
@(negedge clk); rst=0; d=8'hff; @(posedge clk); #1; check(q4===4'd15 && q8===8'd255);
@(negedge clk); rst=0; d=8'h00; @(posedge clk); #1; check(q4===4'd0 && q8===8'd0);

 $display("CHECKS %0d ERRORS %0d",tests,errors);
 if(errors==0) $display("PASS");
 $finish;
end
endmodule
