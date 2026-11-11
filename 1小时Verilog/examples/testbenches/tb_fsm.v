`timescale 1ns/1ps
module tb;
reg clk=0,rst=1,go=0,done=0; wire busy; wire [1:0] state;
integer tests=0,errors=0;
fsm dut(clk,rst,go,done,busy,state);
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
@(posedge clk); #1; check(state===0 && busy===0);
@(negedge clk); rst=0; go=0; done=0; @(posedge clk); #1; check(state===2'd0 && busy===0);
@(negedge clk); rst=0; go=1; done=0; @(posedge clk); #1; check(state===2'd1 && busy===1);
@(negedge clk); rst=0; go=0; done=0; @(posedge clk); #1; check(state===2'd1 && busy===1);
@(negedge clk); rst=0; go=0; done=1; @(posedge clk); #1; check(state===2'd2 && busy===0);
@(negedge clk); rst=0; go=0; done=0; @(posedge clk); #1; check(state===2'd0 && busy===0);
@(negedge clk); rst=0; go=1; done=0; @(posedge clk); #1; check(state===2'd1 && busy===1);
@(negedge clk); rst=0; go=0; done=1; @(posedge clk); #1; check(state===2'd2 && busy===0);
@(negedge clk); rst=0; go=0; done=0; @(posedge clk); #1; check(state===2'd0 && busy===0);

 $display("CHECKS %0d ERRORS %0d",tests,errors);
 if(errors==0) $display("PASS");
 $finish;
end
endmodule
