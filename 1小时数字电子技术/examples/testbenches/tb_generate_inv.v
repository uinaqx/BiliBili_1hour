`timescale 1ns/1ps
module tb;
reg [3:0] a; wire [3:0] y;
integer tests=0,errors=0;
generate_inv dut(a,y);

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
a=4'd0; #3; check(y===4'd15);
a=4'd1; #3; check(y===4'd14);
a=4'd2; #3; check(y===4'd13);
a=4'd3; #3; check(y===4'd12);
a=4'd4; #3; check(y===4'd11);
a=4'd5; #3; check(y===4'd10);
a=4'd6; #3; check(y===4'd9);
a=4'd7; #3; check(y===4'd8);
a=4'd8; #3; check(y===4'd7);
a=4'd9; #3; check(y===4'd6);
a=4'd10; #3; check(y===4'd5);
a=4'd11; #3; check(y===4'd4);
a=4'd12; #3; check(y===4'd3);
a=4'd13; #3; check(y===4'd2);
a=4'd14; #3; check(y===4'd1);
a=4'd15; #3; check(y===4'd0);
 $display("CHECKS %0d ERRORS %0d",tests,errors);
 if(errors==0) $display("PASS");
 $finish;
end
endmodule
