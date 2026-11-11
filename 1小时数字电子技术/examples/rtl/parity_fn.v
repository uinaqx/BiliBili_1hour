module parity_fn(input wire [3:0] a,
  output wire y);
  function parity4;
    input [3:0] value;
    begin parity4 = ^value; end
  endfunction
  assign y = parity4(a);
endmodule
