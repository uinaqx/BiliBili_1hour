module adder(input wire [3:0] a, b,
  output wire [3:0] low,
  output wire [4:0] full);
  assign low = a + b;
  assign full = {1'b0, a} + {1'b0, b};
endmodule
