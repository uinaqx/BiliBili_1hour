module mux2(input wire a, b, sel,
  output wire y);
  assign y = sel ? b : a;
endmodule
