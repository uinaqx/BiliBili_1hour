module reg_param #(parameter WIDTH = 4)(
  input wire clk, rst,
  input wire [WIDTH-1:0] d,
  output reg [WIDTH-1:0] q);
  always @(posedge clk) begin
    if (rst) q <= {WIDTH{1'b0}};
    else     q <= d;
  end
endmodule
