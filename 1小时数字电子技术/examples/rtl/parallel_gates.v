module parallel_gates(input wire a, b,
  output wire y_and, y_or);
  assign y_and = a & b;
  assign y_or  = a | b;
endmodule
