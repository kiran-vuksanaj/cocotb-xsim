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
  output logic [47:0] count_out,
  input wire          incr_in,
  output logic [15:0] cordic_out,
  output logic        cordic_valid
);

  logic [15:0] count;
  // assign count_out = count << 32;
  assign count_out = count;
  always_ff @(posedge clk) begin
    if (rst) begin
      count <= 16'h0;
    end else begin
      if (incr_in) begin
        count <= count + 1;
      end
    end
  end

  assign cordic_valid = 1'bZ;

endmodule
