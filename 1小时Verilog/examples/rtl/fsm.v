module fsm(input wire clk, rst, go, done,
  output wire busy, output reg [1:0] state);
  localparam IDLE=2'd0, RUN=2'd1, WAIT=2'd2;
  reg [1:0] next_state;
  always @(posedge clk) begin
    if (rst) state <= IDLE;
    else     state <= next_state;
  end
  always @(*) begin
    next_state = state;
    case (state)
      IDLE: if (go) next_state = RUN;
      RUN:  if (done) next_state = WAIT;
      WAIT: next_state = IDLE;
      default: next_state = IDLE;
    endcase
  end
  assign busy = (state == RUN);
endmodule
