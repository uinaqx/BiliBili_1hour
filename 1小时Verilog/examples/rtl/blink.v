module blink #(parameter LIMIT = 3)(
  input wire clk, rst, en,
  output reg led, output reg [3:0] count);
  always @(posedge clk) begin
    if (rst) begin count <= 0; led <= 0; end
    else if (en) begin
      if (count == LIMIT-1) begin
        count <= 0;
        led <= ~led;
      end else count <= count + 1'b1;
    end
  end
endmodule
