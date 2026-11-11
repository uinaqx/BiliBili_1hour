module hierarchy(input wire a, b, sel,
  output wire y);
  wire selected;
  mux2 u_mux(.a(a), .b(b), .sel(sel),
             .y(selected));
  assign y = ~selected;
endmodule
