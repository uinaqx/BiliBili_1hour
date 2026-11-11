module vector_demo(input wire [7:0] data,
  output wire [3:0] hi, lo,
  output wire [7:0] swapped);
  assign hi = data[7:4];
  assign lo = data[3:0];
  assign swapped = {lo, hi};
endmodule
