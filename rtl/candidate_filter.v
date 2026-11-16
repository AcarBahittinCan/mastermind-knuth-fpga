module candidate_filter (
    input  wire        clk,
    input  wire        rst,
    input  wire        enable,
    input  wire [15:0] guess,
    input  wire [2:0]  plus_in,
    input  wire [2:0]  minus_in,
    output reg         done
);

    reg [1295:0] candidates;
    reg [10:0]   idx_eval;

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

    wire [15:0] current_code;
    wire [2:0]  su_plus, su_minus;

    assign current_code = idx_to_code(idx_eval);

    scoreUnit #(.CODE_LEN(4)) scoreUnit_inst (
        .code1(guess),
        .code2(current_code),
        .plus(su_plus),
        .minus(su_minus)
    );

    localparam IDLE    = 2'd0;
    localparam RUNNING = 2'd1;
    localparam FINISH  = 2'd2;

    reg [1:0] state;

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            candidates <= {1296{1'b1}};
            idx_eval   <= 11'd0;
            done       <= 1'b0;
            state      <= IDLE;
        end else begin
            case (state)
                IDLE: begin
                    done <= 1'b0;
                    if (enable) begin
                        idx_eval <= 11'd0;
                        state    <= RUNNING;
                    end
                end

                RUNNING: begin
                    if (candidates[idx_eval]) begin
                        if (su_plus != plus_in || su_minus != minus_in)
                            candidates[idx_eval] <= 1'b0;
                    end
                    if (idx_eval == 11'd1295)
                        state <= FINISH;
                    else
                        idx_eval <= idx_eval + 1;
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