`default_nettype none

// Module: matrix_mult
// Purpose: 3x3 matrix multiplier, C = A x B, for the open-source RTL-to-GDS flow.
//          Same behaviour as the UVM version (Design.sv) but with flat ports,
//          because Yosys-based flows do not accept unpacked-array ports.
//
// Timing:  Registered. A and B are sampled on the clock edge where start = 1.
//          After that edge c_flat holds the result and done = 1 (1-cycle latency).
//          done is a one-cycle pulse per start. With start = 0, done = 0 and
//          c_flat holds its last value. Reset is asynchronous, active low.
//
// Packing: element (row i, column j) of a matrix sits at bit offset (i*3 + j) * width
//          a_flat / b_flat : 9 elements, each UQ8.0  (bits [71:0])
//          c_flat          : 9 elements, each UQ20.0 (bits [179:0])
//          Max element value is 3 * 255 * 255 = 195075, which fits in 18 bits.
module matrix_mult (
    input  logic         clk,      // System clock
    input  logic         rst_n,    // Asynchronous reset, active low
    input  logic         start,    // Sample a_flat and b_flat on this clock edge
    input  logic [71:0]  a_flat,   // Matrix A, 9 elements, UQ8.0 each
    input  logic [71:0]  b_flat,   // Matrix B, 9 elements, UQ8.0 each
    output logic [179:0] c_flat,   // Matrix C = A x B, 9 elements, UQ20.0 each
    output logic         done      // High for one cycle after a start edge
);

    logic [179:0] c_calc;      // Combinational A x B, 9 elements, UQ20.0 each
    logic [179:0] c_next;      // Next value of c_flat
    logic         done_next;   // Next value of done

    // One multiply-accumulate unit per output element:
    // C[i][j] = A[i][0]*B[0][j] + A[i][1]*B[1][j] + A[i][2]*B[2][j]
    genvar gi;
    genvar gj;
    generate
        for (gi = 0; gi < 3; gi = gi + 1) begin : g_row
            for (gj = 0; gj < 3; gj = gj + 1) begin : g_col
                logic [15:0] prod0;   // A[gi][0] * B[0][gj], UQ16.0
                logic [15:0] prod1;   // A[gi][1] * B[1][gj], UQ16.0
                logic [15:0] prod2;   // A[gi][2] * B[2][gj], UQ16.0

                assign prod0 = a_flat[(gi*3 + 0)*8 +: 8] * b_flat[(0*3 + gj)*8 +: 8];
                assign prod1 = a_flat[(gi*3 + 1)*8 +: 8] * b_flat[(1*3 + gj)*8 +: 8];
                assign prod2 = a_flat[(gi*3 + 2)*8 +: 8] * b_flat[(2*3 + gj)*8 +: 8];

                assign c_calc[(gi*3 + gj)*20 +: 20] = {4'd0, prod0} + {4'd0, prod1} + {4'd0, prod2};
            end
        end
    endgenerate

    // Next-state logic: load the new result on start, otherwise hold
    always_comb begin
        c_next    = start ? c_calc : c_flat;
        done_next = start;
    end

    // Registers: asynchronous active-low reset, simple assignments only
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            c_flat <= 180'd0;
            done   <= 1'b0;
        end else begin
            c_flat <= c_next;
            done   <= done_next;
        end
    end

endmodule

`default_nettype wire
