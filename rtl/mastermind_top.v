module mastermind_top (
    input  wire        clk,
    input  wire        rst,
    input  wire [15:0] secret,
    output reg  [15:0] guess,
    output reg  [2:0]  plus_out,
    output reg  [2:0]  minus_out,
    output reg  [3:0]  attempts,
    output reg         done
);

    wire [2:0] su_plus, su_minus;

    scoreUnit #(.CODE_LEN(4)) scoreUnit_inst (
        .code1(guess),
        .code2(secret),
        .plus(su_plus),
        .minus(su_minus)
    );

    reg         cf_enable;
    wire        cf_done;

    candidate_filter cf_inst (
        .clk(clk),
        .rst(rst),
        .enable(cf_enable),
        .guess(guess),
        .plus_in(plus_out),
        .minus_in(minus_out),
        .done(cf_done)
    );

    reg         mm_enable;
    wire [15:0] mm_best_guess;
    wire        mm_done;

    minimax_unit mm_inst (
        .clk(clk),
        .rst(rst),
        .enable(mm_enable),
        .candidates(cf_inst.candidates),
        .best_guess(mm_best_guess),
        .done(mm_done)
    );

    localparam IDLE    = 3'd0;
    localparam SCORE   = 3'd1;
    localparam CHECK   = 3'd2;
    localparam FILTER  = 3'd3;
    localparam MINIMAX = 3'd4;
    localparam DONE    = 3'd5;

    reg [2:0] state;

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            guess     <= 16'h1122;
            plus_out  <= 3'd0;
            minus_out <= 3'd0;
            attempts  <= 4'd0;
            done      <= 1'b0;
            cf_enable <= 1'b0;
            mm_enable <= 1'b0;
            state     <= IDLE;
        end else begin
            cf_enable <= 1'b0;
            mm_enable <= 1'b0;

            case (state)

                IDLE: begin
                    guess    <= 16'h1122;
                    attempts <= 4'd0;
                    done     <= 1'b0;
                    state    <= SCORE;
                end

                SCORE: begin
                    plus_out  <= su_plus;
                    minus_out <= su_minus;
                    attempts  <= attempts + 1;
                    state     <= CHECK;
                end

                CHECK: begin
                    if (plus_out == 3'd4) begin
                        state <= DONE;
                    end else begin
                        cf_enable <= 1'b1;
                        state     <= FILTER;
                    end
                end

                FILTER: begin
                    if (cf_done) begin
                        mm_enable <= 1'b1;
                        state     <= MINIMAX;
                    end
                end

                MINIMAX: begin
                    if (mm_done) begin
                        guess <= mm_best_guess;
                        state <= SCORE;
                    end
                end

                DONE: begin
                    done  <= 1'b1;
                    state <= DONE;
                end

                default: state <= IDLE;
            endcase
        end
    end

endmodule