`timescale 1ns/1ps
module tb;
reg [1:0] sel; wire [3:0] y;
integer tests=0,errors=0;
decoder dut(sel,y);

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
sel=2'd0; #4; check(y===4'd1);
sel=2'd1; #4; check(y===4'd2);
sel=2'd2; #4; check(y===4'd4);
sel=2'd3; #4; check(y===4'd8);
 $display("CHECKS %0d ERRORS %0d",tests,errors);
 if(errors==0) $display("PASS");
 $finish;
end
endmodule
