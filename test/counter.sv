`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 01/13/2025 03:17:49 PM
// Design Name: 
// Module Name: counter
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module counter(
  input wire          clk,
  input wire          rst,
  output logic [31:0] count_out,
  input wire          incr_in
);

  always_ff @(posedge clk) begin
    if (rst) begin
      count_out <= 32'h0;
    end else begin
      if (incr_in) begin
        count_out <= count_out + 1;
      end
    end
  end
endmodule
