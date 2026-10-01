
`timescale 1ns/1ps

module tb;
    reg clk = 0;
    reg rst_n = 0;
    reg [7:0] tx_data = 8'h00;
    reg tx_start = 0;
    wire tx_out;
    wire tx_busy;

    uart_tx #(
        .CLOCK_FREQ(100000000),
        .BAUD_RATE(115200)
    ) dut (
        .clk(clk),
        .rst_n(rst_n),
        .tx_data(tx_data),
        .tx_start(tx_start),
        .tx_out(tx_out),
        .tx_busy(tx_busy)
    );

    always #5 clk = ~clk;

    integer i;
    initial begin
        $display("Starting UART TX testbench");
        #10 rst_n = 1;
        tx_data = 8'h41;   // 'A'
        #20 tx_start = 1;
        #10 tx_start = 0;

        for (i = 0; i < 200; i = i + 1) begin
            #10;
            if (i == 100) begin
                tx_data = 8'h42; // 'B'
                tx_start = 1;
            end
            if (i == 110) begin
                tx_start = 0;
            end
        end

        #200000;
        $display("UART TX testbench finished");
        $finish;
    end
endmodule
