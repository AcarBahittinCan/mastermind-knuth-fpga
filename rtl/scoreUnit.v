module scoreUnit #(parameter CODE_LEN = 5) (
    input  [(CODE_LEN*4)-1:0] code1,
    input  [(CODE_LEN*4)-1:0] code2,
    output [2:0] plus,
    output [2:0] minus
);

    wire [3:0] guess [CODE_LEN-1:0];
    wire [3:0] secret [CODE_LEN-1:0];

    genvar k;
    generate
        for (k = 0; k < CODE_LEN; k = k + 1) begin : extract
            assign guess[k] = code1[(CODE_LEN-1-k)*4 +: 4];
            assign secret[k] = code2[(CODE_LEN-1-k)*4 +: 4];
        end
    endgenerate

    reg [CODE_LEN-1:0] guess_used;
    reg [CODE_LEN-1:0] secret_used;
    reg [2:0] plus_r;
    reg [2:0] minus_r;

    integer i, j;

    always @(*) begin
        guess_used  = 0;
        secret_used = 0;
        plus_r      = 3'd0;
        minus_r     = 3'd0;

        for (i = 0; i < CODE_LEN; i = i + 1) begin
            if (guess[i] == secret[i]) begin
                plus_r         = plus_r + 1;
                guess_used[i]  = 1'b1;
                secret_used[i] = 1'b1;
            end
        end

        for (i = 0; i < CODE_LEN; i = i + 1) begin
            if (!guess_used[i]) begin
                for (j = 0; j < CODE_LEN; j = j + 1) begin
                    if (!guess_used[i] && !secret_used[j] && guess[i] == secret[j]) begin
                        minus_r        = minus_r + 1;
                        guess_used[i]  = 1'b1;
                        secret_used[j] = 1'b1;
                    end
                end
            end
        end
    end

    assign plus  = plus_r;
    assign minus = minus_r;

endmodule