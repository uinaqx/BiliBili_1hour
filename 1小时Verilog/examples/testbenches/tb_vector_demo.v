`timescale 1ns/1ps
module tb;
reg [7:0] data; wire [3:0] hi,lo; wire [7:0] swapped;
integer tests=0,errors=0;
vector_demo dut(data,hi,lo,swapped);

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
data=8'h00; #4; check(hi===4'd0); check(lo===4'd0); check(swapped===8'h00);
data=8'ha5; #4; check(hi===4'd10); check(lo===4'd5); check(swapped===8'h5a);
data=8'h3c; #4; check(hi===4'd3); check(lo===4'd12); check(swapped===8'hc3);
data=8'hff; #4; check(hi===4'd15); check(lo===4'd15); check(swapped===8'hff);
 $display("CHECKS %0d ERRORS %0d",tests,errors);
 if(errors==0) $display("PASS");
 $finish;
end
endmodule
