module latch_fixed(input wire en, d,
  output reg q);
  always @(*) begin
    q = 1'b0;
    if (en) q = d;
  end
endmodule
