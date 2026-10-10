`timescale 1ns / 1ps

module tb_exoplanet_bls_top;

    reg clk;
    reg rst;
    reg start;

    wire busy;
    wire done;
    wire [15:0] best_period_samples;
    wire [7:0] best_duration_samples;
    wire signed [31:0] best_depth_q;
    wire [63:0] best_score;

    integer cycle_count;
    real detected_period_days;
    real detected_duration_days;
    real estimated_depth_fraction;

    exoplanet_bls_top #(
        .N_SAMPLES(1350),
        .TRUE_PERIOD_SAMPLES(185),
        .TRUE_EPOCH_SAMPLES(60),
        .TRUE_DURATION_SAMPLES(6),
        .TRUE_DEPTH_Q(10),
        .FLUX_SCALE(1000),
        .MIN_PERIOD_SAMPLES(100),
        .MAX_PERIOD_SAMPLES(300),
        .MIN_DURATION_SAMPLES(3),
        .MAX_DURATION_SAMPLES(10),
        .DURATION_STEP_SAMPLES(2)
    ) dut (
        .clk(clk),
        .rst(rst),
        .start(start),
        .busy(busy),
        .done(done),
        .best_period_samples(best_period_samples),
        .best_duration_samples(best_duration_samples),
        .best_depth_q(best_depth_q),
        .best_score(best_score)
    );

    // 100 MHz clock: 10 ns period
    initial begin
        clk = 1'b0;
        forever #5 clk = ~clk;
    end

    initial begin
        rst = 1'b1;
        start = 1'b0;
        cycle_count = 0;

        $display("");
        $display("==============================================================");
        $display(" EXOPLANET TRANSIT DETECTION - BLS RTL SIMULATION");
        $display("==============================================================");
        $display("Clock frequency            : 100 MHz");
        $display("Injected true period       : 3.70 days (185 samples)");
        $display("Injected transit duration  : 0.12 days (6 samples)");
        $display("Injected transit depth     : 1%%");
        $display("Number of light-curve data : 1350");
        $display("Starting simulation...");
        $display("--------------------------------------------------------------");

        repeat (5) @(negedge clk);
        rst = 1'b0;

        repeat (3) @(negedge clk);
        start = 1'b1;
        @(negedge clk);
        start = 1'b0;
        $display("[%0t ns] START pulse sent; waiting for processing...", $time);

        // Wait for completion, with a generous timeout.
        while ((done !== 1'b1) && (cycle_count < 2000000)) begin
            @(negedge clk);
            cycle_count = cycle_count + 1;
        end

        if (done === 1'b1) begin
            detected_period_days = best_period_samples * 0.02;
            detected_duration_days = best_duration_samples * 0.02;
            estimated_depth_fraction = best_depth_q / 1000.0;

            $display("");
            $display("===================== FINAL RESULTS ==========================");
            $display("Simulation status           : DONE");
            $display("Cycles waited                : %0d", cycle_count);
            $display("Search runtime (simulated)   : %0.3f ms",
                     cycle_count * 0.00001);
            $display("--------------------------------------------------------------");
            $display("Detected period (samples)    : %0d", best_period_samples);
            $display("Detected period (days)       : %0.5f", detected_period_days);
            $display("Detected duration (samples)  : %0d", best_duration_samples);
            $display("Detected duration (days)     : %0.5f", detected_duration_days);
            $display("Estimated depth (flux units) : %0d", best_depth_q);
            $display("Estimated depth (fraction)   : %0.6f",
                     estimated_depth_fraction);
            $display("Best score                   : %0d", best_score);
            $display("--------------------------------------------------------------");
            $display("Injected period (days)       : 3.70000");
            $display("Injected duration (days)     : 0.12000");
            $display("Injected depth (fraction)    : 0.010000");

            if (best_period_samples != 0) begin
                $display("Absolute period error (days) : %0.5f",
                         (detected_period_days >= 3.70) ?
                         (detected_period_days - 3.70) :
                         (3.70 - detected_period_days));
            end else begin
                $display("WARNING: No valid period candidate was reported.");
            end

            $display("==============================================================");
            $display("NOTE: Results are diagnostic only. The current RTL scaffold");
            $display("does not yet implement the complete Python BLS window search.");
            $display("==============================================================");
        end else begin
            $display("");
            $display("===================== SIMULATION ERROR ======================");
            $display("ERROR: Timeout waiting for done.");
            $display("Cycles waited : %0d", cycle_count);
            $display("busy=%b done=%b state=%0d", busy, done, dut.state);
            $display("==============================================================");
            $fatal(1, "Simulation timeout");
        end

        #20;
        $finish;
    end

endmodule
