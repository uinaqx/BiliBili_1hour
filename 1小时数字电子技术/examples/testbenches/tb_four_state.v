module tb;
reg a; wire undriven; integer errors=0;
initial begin
  a=1'bx; #1;
  if ((a==1'b0)!==1'bx) errors=errors+1;
  if ((a===1'bx)!==1'b1) errors=errors+1;
  if (undriven!==1'bz) errors=errors+1;
  $display("a=%b undriven=%b ==0:%b ===x:%b",a,undriven,a==0,a===1'bx);
  $display("CHECKS 3 ERRORS %0d",errors);
  if (errors==0) $display("PASS"); $finish;
end
endmodule