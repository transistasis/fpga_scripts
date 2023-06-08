module dut_with_parameters 
                                      #(
  parameter WIDTH
  =
         12,
  parameter HEIGHT              = 32,
         parameter   TEST )
(
  input  logic        clk_i,
   input logic rst_i,
  input   logic [1:0]  rx_i,
      input           logic [4:0][1:0]             array_a_i,
   input    logic [4:0]      
        [1:0]   
                   [7:0]             array_b_i,
  output logic [1:0]  tx_o,
   inout  tri          sda_bi,
  inout  
  wire         
  scl_bi );

endmodule : dut_with_parameters
