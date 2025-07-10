`timescale 1 ns / 1 ps

module fifo_wrap(
  input wire clk
);

  fifo_dut_sync dut(
    .s_axis_aclk(clk)
  );
  
endmodule
