module generate_inv #(parameter WIDTH = 4)(
  input wire [WIDTH-1:0] a,
  output wire [WIDTH-1:0] y);
  genvar i;
  generate
    for (i=0; i<WIDTH; i=i+1) begin: bits
      assign y[i] = ~a[i];
    end
  endgenerate
endmodule
