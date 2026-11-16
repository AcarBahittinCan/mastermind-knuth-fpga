// mastermind_top_tb.v
// Verbose testbench: shows every guess, score
// Tests 5 different secrets

module mastermind_top_tb;

    reg         clk, rst;
    reg  [15:0] secret;
    wire [15:0] guess;
    wire [2:0]  plus_out, minus_out;
    wire [3:0]  attempts;
    wire        done;

    mastermind_top dut (
        .clk(clk), .rst(rst),
        .secret(secret),
        .guess(guess),
        .plus_out(plus_out),
        .minus_out(minus_out),
        .attempts(attempts),
        .done(done)
    );

    always #5 clk = ~clk;

    reg [3:0] prev_attempts;
    always @(posedge clk) begin
        if (rst) begin
            prev_attempts <= 0;
        end else if (attempts != prev_attempts && attempts > 0) begin
            $display("  attempt %0d | guess=%h | plus=%0d minus=%0d",
                attempts, guess, plus_out, minus_out);
            prev_attempts <= attempts;
        end
    end

    task solve;
        input [15:0] sec;
        input [63:0] label;
        begin
            rst = 1; secret = sec;
            repeat(4) @(posedge clk);
            rst = 0;

            $display("----------------------------------------");
            $display("SECRET: %s (%h)", label, sec);
            $display("----------------------------------------");

            wait(done);
            @(posedge clk);

            $display("");
        end
    endtask

    initial begin
        clk = 0; rst = 1;
        #20;

        solve(16'h1122, "1122 (first guess)   ");

        solve(16'h6666, "6666 (all same)      ");

        solve(16'h3614, "3614                 ");

        solve(16'h2211, "2211 (reverse 1122)  ");

        solve(16'h1362, "1362                 ");

        $display("========================================");
        $display("ALL TESTS DONE");
        $display("========================================");
        $finish;
    end

endmodule