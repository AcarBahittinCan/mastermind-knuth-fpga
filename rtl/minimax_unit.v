module minimax_unit (
    input  wire          clk,
    input  wire          rst,
    input  wire          enable,
    input  wire [1295:0] candidates,
    output reg  [15:0]   best_guess,
    output reg           done
);

    function [15:0] idx_to_code;
        input [10:0] i;
        reg [10:0] tmp;
        reg [3:0]  d0, d1, d2, d3;
        begin
            tmp = i;
            d3 = (tmp % 6) + 1; tmp = tmp / 6;
            d2 = (tmp % 6) + 1; tmp = tmp / 6;
            d1 = (tmp % 6) + 1; tmp = tmp / 6;
            d0 = (tmp % 6) + 1;
            idx_to_code = {d0, d1, d2, d3};
        end
    endfunction

    wire [15:0] su_code1, su_code2;
    wire [2:0]  su_plus, su_minus;

    reg [10:0] outer_idx;
    reg [10:0] inner_idx;

    assign su_code1 = idx_to_code(outer_idx);
    assign su_code2 = idx_to_code(inner_idx);

    scoreUnit #(.CODE_LEN(4)) scoreUnit_inst (
        .code1(su_code1),
        .code2(su_code2),
        .plus(su_plus),
        .minus(su_minus)
    );

    reg [10:0] group_count [0:24];
    reg [10:0] best_worst_case;
    reg        best_is_candidate;

    reg [10:0] worst_case;
    reg        cur_is_cand;
    reg        do_update;

    localparam IDLE    = 3'd0;
    localparam INNER   = 3'd1;
    localparam WAIT    = 3'd2;
    localparam COMPARE = 3'd3;
    localparam CLEAR   = 3'd4;
    localparam FINISH  = 3'd5;

    reg [2:0] state;
    integer i;

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            outer_idx         <= 11'd0;
            inner_idx         <= 11'd0;
            best_guess        <= 16'h1122;
            best_worst_case   <= 11'h7FF;
            best_is_candidate <= 1'b0;
            done              <= 1'b0;
            state             <= IDLE;
            for (i = 0; i < 25; i = i + 1)
                group_count[i] <= 0;
        end else begin
            case (state)

                IDLE: begin
                    done <= 1'b0;
                    if (enable) begin
                        outer_idx         <= 11'd0;
                        inner_idx         <= 11'd0;
                        best_worst_case   <= 11'h7FF;
                        best_is_candidate <= 1'b0;
                        state             <= INNER;
                    end
                end

                INNER: begin
                    if (candidates[inner_idx])
                        group_count[su_plus * 5 + su_minus] <=
                            group_count[su_plus * 5 + su_minus] + 1;
                    if (inner_idx == 11'd1295)
                        state <= WAIT;
                    else
                        inner_idx <= inner_idx + 1;
                end
                
                WAIT: begin
                    state <= COMPARE;
                end

                COMPARE: begin
                
                    worst_case = 11'd0;
                    for (i = 0; i < 25; i = i + 1)
                        if (group_count[i] > worst_case)
                            worst_case = group_count[i];

                    cur_is_cand = candidates[outer_idx];
                    do_update   = 1'b0;

                    if (worst_case < best_worst_case)
                        do_update = 1'b1;
                    else if (worst_case == best_worst_case)
                        if (cur_is_cand && !best_is_candidate)
                            do_update = 1'b1;

                    if (do_update) begin
                        best_guess        <= idx_to_code(outer_idx);
                        best_worst_case   <= worst_case;
                        best_is_candidate <= cur_is_cand;
                    end

                    state <= CLEAR;
                end
                
                CLEAR: begin
                    for (i = 0; i < 25; i = i + 1)
                        group_count[i] <= 0;

                    if (outer_idx == 11'd1295)
                        state <= FINISH;
                    else begin
                        outer_idx <= outer_idx + 1;
                        inner_idx <= 11'd0;
                        state     <= INNER;
                    end
                end

                FINISH: begin
                    done  <= 1'b1;
                    state <= IDLE;
                end

                default: state <= IDLE;
            endcase
        end
    end

endmodule