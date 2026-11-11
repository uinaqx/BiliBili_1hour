module tb;
reg [3:0] narrow_value; reg signed [3:0] s;
reg [3:0] u; integer errors=0;
reg signed [3:0] arithmetic; reg [3:0] logical_shift;
initial begin
 narrow_value=4'b1111+4'b0001; s=4'b1100; u=4'b1100;
 arithmetic=s>>>1; logical_shift=u>>1; #1;
 if (narrow_value!==0) errors=errors+1;
 if (arithmetic!==4'b1110) errors=errors+1;
 if (logical_shift!==4'b0110) errors=errors+1;
 $display("narrow=%b arithmetic=%b logical=%b",narrow_value,arithmetic,logical_shift);
 $display("CHECKS 3 ERRORS %0d",errors);
 if(errors==0) $display("PASS"); $finish;
end
endmodule