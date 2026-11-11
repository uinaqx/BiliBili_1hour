module decoder(input wire [1:0] sel,
  output reg [3:0] y);
  always @(*) begin
    case (sel)
      2'b00: y = 4'b0001;
      2'b01: y = 4'b0010;
      2'b10: y = 4'b0100;
      default: y = 4'b1000;
    endcase
  end
endmodule
