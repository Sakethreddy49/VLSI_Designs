`default_nettype none

// Module: handshake_dut
// Purpose: Validate that VALID arrives exactly one clock after READY.
// Timing: Asynchronous active-low reset; intended first-pass clock period is 10 ns.
module handshake_dut (
    input  logic clk,             // System clock
    input  logic rst_n,           // Asynchronous active-low reset
    input  logic ready,           // Request/ready event observed in the current cycle
    input  logic valid,           // Response/valid event observed in the current cycle
    output logic handshake_ok,    // One-cycle pulse for an exact one-cycle-late VALID
    output logic error_early,     // One-cycle pulse when VALID is same-cycle with READY
    output logic error_late,      // One-cycle pulse when VALID arrives after the deadline
    output logic error_missing    // One-cycle pulse when VALID never arrives
);

    typedef enum logic [1:0] {
        IDLE     = 2'b00,
        WAIT_VAL = 2'b01,
        DONE     = 2'b10,
        ERR      = 2'b11
    } state_t;

    state_t state;               // Current protocol-validation state
    logic [3:0] wait_cnt;         // Elapsed wait counter, UQ4.0

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state         <= IDLE;
            wait_cnt      <= 4'd0;
            handshake_ok  <= 1'b0;
            error_early   <= 1'b0;
            error_late    <= 1'b0;
            error_missing <= 1'b0;
        end else begin
            handshake_ok  <= 1'b0;
            error_early   <= 1'b0;
            error_late    <= 1'b0;
            error_missing <= 1'b0;

            case (state)
                IDLE: begin
                    wait_cnt <= 4'd0;
                    if (ready) begin
                        if (valid) begin
                            error_early <= 1'b1;
                            state        <= IDLE;
                        end else begin
                            state <= WAIT_VAL;
                        end
                    end
                end

                WAIT_VAL: begin
                    wait_cnt <= wait_cnt + 4'd1;
                    if (wait_cnt == 4'd0) begin
                        if (valid) begin
                            handshake_ok <= 1'b1;
                            state        <= IDLE;
                        end else begin
                            state <= ERR;
                        end
                    end
                end

                ERR: begin
                    wait_cnt <= wait_cnt + 4'd1;
                    if (valid) begin
                        error_late <= 1'b1;
                        state      <= IDLE;
                    end else if (wait_cnt >= 4'd4) begin
                        error_missing <= 1'b1;
                        state          <= IDLE;
                    end
                end

                DONE: begin
                    state <= IDLE;
                end

                default: begin
                    state <= IDLE;
                end
            endcase
        end
    end
endmodule

`default_nettype wire
