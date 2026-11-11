`timescale 1ns/1ps
module tb;
reg a,b,sel; wire y_and, y_or;
integer tests=0,errors=0;
parallel_gates dut(.a(a),.b(b),.y_and(y_and),.y_or(y_or));

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
a=0; b=0; sel=0; #4; check(y_and===1'b0); check(y_or===1'b0);
a=0; b=1; sel=0; #4; check(y_and===1'b0); check(y_or===1'b1);
a=1; b=0; sel=0; #4; check(y_and===1'b0); check(y_or===1'b1);
a=1; b=1; sel=0; #4; check(y_and===1'b1); check(y_or===1'b1);
 $display("CHECKS %0d ERRORS %0d",tests,errors);
 if(errors==0) $display("PASS");
 $finish;
end
endmodule
