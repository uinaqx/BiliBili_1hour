module pipeline(input wire clk, rst, d,
  output reg q1, q2);
  always @(posedge clk) begin
    if (rst) begin q1 <= 0; q2 <= 0; end
    else begin
      q1 <= d;
      q2 <= q1;
    end
  end
endmodule
