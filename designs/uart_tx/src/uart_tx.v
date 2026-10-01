module uart_tx #(
    parameter CLKS_PER_BIT = 868   // 100 MHz / 115200 baud
)(
    input  wire       clk,
    input  wire       rst_n,
    input  wire [7:0] tx_data,
    input  wire       tx_start,
    output reg        tx,
    output wire       busy
);
    localparam IDLE = 2'd0, START = 2'd1, DATA = 2'd2, STOP = 2'd3;

    reg [1:0]  state;
    reg [15:0] clk_cnt;
    reg [2:0]  bit_idx;
    reg [7:0]  shreg;

    assign busy = (state != IDLE);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE; tx <= 1'b1;
            clk_cnt <= 16'd0; bit_idx <= 3'd0; shreg <= 8'd0;
        end else begin
            case (state)
                IDLE: begin
                    tx <= 1'b1; clk_cnt <= 16'd0; bit_idx <= 3'd0;
                    if (tx_start) begin shreg <= tx_data; state <= START; end
                end
                START: begin
                    tx <= 1'b0;
                    if (clk_cnt == CLKS_PER_BIT-1) begin clk_cnt <= 16'd0; state <= DATA; end
                    else clk_cnt <= clk_cnt + 16'd1;
                end
                DATA: begin
                    tx <= shreg[bit_idx];
                    if (clk_cnt == CLKS_PER_BIT-1) begin
                        clk_cnt <= 16'd0;
                        if (bit_idx == 3'd7) state <= STOP;
                        else bit_idx <= bit_idx + 3'd1;
                    end else clk_cnt <= clk_cnt + 16'd1;
                end
                STOP: begin
                    tx <= 1'b1;
                    if (clk_cnt == CLKS_PER_BIT-1) begin clk_cnt <= 16'd0; state <= IDLE; end
                    else clk_cnt <= clk_cnt + 16'd1;
                end
            endcase
        end
    end
endmodule