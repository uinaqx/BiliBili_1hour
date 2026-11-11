module mux_always(input wire a, b, sel,
  output reg y);
  always @(*) begin
    if (sel) y = b;
    else     y = a;
  end
endmodule
