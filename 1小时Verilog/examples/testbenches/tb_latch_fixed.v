`timescale 1ns/1ps
module tb;
reg en,d; wire q;
integer tests=0,errors=0;
latch_fixed dut(en,d,q);

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
en=1; d=0; #4; check(q===0); d=1; #4; check(q===1); en=0; d=0; #4; check(q===0); d=1; #4; check(q===0);
 $display("CHECKS %0d ERRORS %0d",tests,errors);
 if(errors==0) $display("PASS");
 $finish;
end
endmodule
