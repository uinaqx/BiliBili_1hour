`timescale 1ns/1ps
module tb;
reg [3:0] a,b; wire [3:0] bit_and; wire logic_and,parity;
integer tests=0,errors=0;
operators dut(a,b,bit_and,logic_and,parity);

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
a=4'd0; b=4'd3; #4; check(bit_and===4'd0); check(logic_and===1'b0); check(parity===1'b0);
a=4'd2; b=4'd1; #4; check(bit_and===4'd0); check(logic_and===1'b1); check(parity===1'b1);
a=4'd6; b=4'd3; #4; check(bit_and===4'd2); check(logic_and===1'b1); check(parity===1'b0);
a=4'd15; b=4'd10; #4; check(bit_and===4'd10); check(logic_and===1'b1); check(parity===1'b0);
a=4'd8; b=4'd0; #4; check(bit_and===4'd0); check(logic_and===1'b0); check(parity===1'b1);
 $display("CHECKS %0d ERRORS %0d",tests,errors);
 if(errors==0) $display("PASS");
 $finish;
end
endmodule
