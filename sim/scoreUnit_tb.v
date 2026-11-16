module scoreUnit_tb;

    reg  [19:0] code1, code2;
    wire [2:0]  plus, minus;

    scoreUnit #(.CODE_LEN(5)) scoreUnit (
        .code1(code1),
        .code2(code2),
        .plus(plus),
        .minus(minus)
    );

    task check;
        input [19:0] c1, c2;
        input [2:0]  exp_plus, exp_minus;
        input [89:0] label;
        begin
            code1 = c1; code2 = c2;
            #10;
            if (plus == exp_plus && minus == exp_minus)
                $display("PASS [%s] plus=%0d minus=%0d", label, plus, minus);
            else
                $display("FAIL [%s] got plus=%0d minus=%0d, expected plus=%0d minus=%0d",
                          label, plus, minus, exp_plus, exp_minus);
        end
    endtask

    initial begin
        $display("=== scoreUnit testbench (CODE_LEN=5) ===");
        check(20'h01234, 20'h01234, 3'd5, 3'd0, "ALL_PLUS ");
        check(20'h01234, 20'h56789, 3'd0, 3'd0, "NO_MATCH ");
        check(20'h01234, 20'h10234, 3'd3, 3'd2, "PART_MTCH");
        check(20'h00112, 20'h11200, 3'd0, 3'd5, "ALL_MINUS");
        check(20'h01234, 20'h04321, 3'd1, 3'd4, "MIX_1    ");
        check(20'h00000, 20'h00000, 3'd5, 3'd0, "ALL_ZERO ");
        check(20'h11111, 20'h11112, 3'd4, 3'd0, "FOUR_PLUS");
        check(20'h12345, 20'h54321, 3'd1, 3'd4, "REVERSE  ");
        $display("=== done ===");
        $finish;
    end

endmodule