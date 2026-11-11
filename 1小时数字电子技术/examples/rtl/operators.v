module operators(input wire [3:0] a, b,
  output wire [3:0] bit_and,
  output wire logic_and, parity);
  assign bit_and = a & b;
  assign logic_and = a && b;
  assign parity = ^a;
endmodule
