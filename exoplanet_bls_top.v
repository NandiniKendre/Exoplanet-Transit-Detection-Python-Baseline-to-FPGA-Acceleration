`timescale 1ns / 1ps
// Exoplanet transit detection: synthesizable BLS-style RTL baseline
// Language: Verilog-2001 (Vivado)
// Notes:
//  * This is a hardware-oriented simplified baseline, not bit-equivalent to NumPy.
//  * Uses fixed-point/integer arithmetic and a sequential FSM.
//  * Light curve is generated on-chip as a deterministic box transit plus optional
//    deterministic pseudo-noise. It does not implement Python's Gaussian RNG.
//  * Period search uses integer sample periods (100..300 samples, step 1).
//    This is intentionally different from the Python's 400 floating-point periods.
//  * Score comparison uses a scaled integer proxy: n_in*n_out*depth^2.
//    Variance normalization is omitted because it is constant across candidates.
//  * Validate and refine before making scientific claims.

module exoplanet_bls_top #(
    parameter integer N_SAMPLES = 1350,
    parameter integer TRUE_PERIOD_SAMPLES = 185, // 3.70 days / 0.02 day
    parameter integer TRUE_EPOCH_SAMPLES  = 60,  // 1.20 days / 0.02 day
    parameter integer TRUE_DURATION_SAMPLES = 6, // 0.12 days / 0.02 day
    parameter integer TRUE_DEPTH_Q = 10,          // 1% of flux scale 1000
    parameter integer FLUX_SCALE = 1000,
    parameter integer MIN_PERIOD_SAMPLES = 100,  // 2 days
    parameter integer MAX_PERIOD_SAMPLES = 300,  // 6 days
    parameter integer MIN_DURATION_SAMPLES = 3,  // 0.06 days
    parameter integer MAX_DURATION_SAMPLES = 10, // 0.20 days
    parameter integer DURATION_STEP_SAMPLES = 2
)(
    input  wire        clk,
    input  wire        rst,
    input  wire        start,
    output reg         busy,
    output reg         done,
    output reg [15:0]  best_period_samples,
    output reg [7:0]   best_duration_samples,
    output reg signed [31:0] best_depth_q,
    output reg [63:0]  best_score
);

    localparam [3:0]
        S_IDLE       = 4'd0,
        S_GEN        = 4'd1,
        S_INIT_SEARCH= 4'd2,
        S_SCAN       = 4'd3,
        S_SCORE      = 4'd4,
        S_NEXT_DUR   = 4'd5,
        S_NEXT_PER   = 4'd6,
        S_FINISH     = 4'd7;

    reg [3:0] state;

    // Flux stored as unsigned integer flux*1000. Nominal flux is 1000.
    reg [10:0] flux_mem [0:N_SAMPLES-1];

    reg [15:0] gen_idx;
    reg [15:0] period_samples;
    reg [7:0]  duration_samples;
    reg [15:0] scan_idx;
    reg [15:0] transit_count;
    reg signed [31:0] transit_sum;
    reg [31:0] total_sum;

    reg [15:0] win_start;
    reg [15:0] win_end;
    reg [15:0] phase_samples;
    reg [15:0] n_in;
    reg [15:0] n_out;
    reg signed [31:0] sum_in;
    reg signed [31:0] sum_out;
    reg signed [31:0] mean_in_q;
    reg signed [31:0] mean_out_q;
    reg signed [31:0] depth_q;

    reg [63:0] score_candidate;
    reg [63:0] score_temp;
    reg [31:0] abs_depth;
    reg [63:0] depth_squared;

    integer k;
    integer dist;
    integer noise_term;
    integer signed sample_value;
    integer signed depth_tmp;

    // Deterministic small pseudo-noise, generated combinationally from sample index.
    // This is reproducible but is NOT Gaussian noise.
    function integer pseudo_noise;
        input integer idx;
        integer v;
        begin
            v = (idx * 37 + 17) % 7;
            pseudo_noise = v - 3; // -3..+3 flux units
        end
    endfunction

    // Generate the synthetic light curve, then search candidate periods/durations.
    // A candidate window is tested at every observed phase, matching the broad
    // search structure of the Python baseline but using integer sample periods.
    always @(posedge clk) begin
        if (rst) begin
            state <= S_IDLE;
            busy <= 1'b0;
            done <= 1'b0;
            gen_idx <= 0;
            period_samples <= MIN_PERIOD_SAMPLES;
            duration_samples <= MIN_DURATION_SAMPLES;
            scan_idx <= 0;
            transit_count <= 0;
            transit_sum <= 0;
            total_sum <= 0;
            win_start <= 0;
            win_end <= 0;
            phase_samples <= 0;
            n_in <= 0;
            n_out <= 0;
            sum_in <= 0;
            sum_out <= 0;
            mean_in_q <= 0;
            mean_out_q <= 0;
            depth_q <= 0;
            score_candidate <= 0;
            score_temp <= 0;
            abs_depth <= 0;
            depth_squared <= 0;
            best_period_samples <= 0;
            best_duration_samples <= 0;
            best_depth_q <= 0;
            best_score <= 0;
        end else begin
            done <= 1'b0;
            case (state)
                S_IDLE: begin
                    busy <= 1'b0;
                    if (start) begin
                        busy <= 1'b1;
                        gen_idx <= 0;
                        best_score <= 0;
                        best_period_samples <= 0;
                        best_duration_samples <= 0;
                        best_depth_q <= 0;
                        state <= S_GEN;
                    end
                end

                S_GEN: begin
                    // Box-shaped transit: nearest phase to epoch in integer samples.
                    // Flux scale = 1000; injected depth = TRUE_DEPTH_Q (default 10).
                    dist = (gen_idx - TRUE_EPOCH_SAMPLES) % TRUE_PERIOD_SAMPLES;
                    if (dist < 0)
                        dist = dist + TRUE_PERIOD_SAMPLES;
                    if (dist > TRUE_PERIOD_SAMPLES/2)
                        dist = dist - TRUE_PERIOD_SAMPLES;

                    noise_term = pseudo_noise(gen_idx);
                    sample_value = FLUX_SCALE + noise_term;
                    if ((dist <= (TRUE_DURATION_SAMPLES/2)) &&
                        (dist >= -(TRUE_DURATION_SAMPLES/2)))
                        sample_value = sample_value - TRUE_DEPTH_Q;

                    if (sample_value < 0)
                        flux_mem[gen_idx] <= 0;
                    else if (sample_value > 2047)
                        flux_mem[gen_idx] <= 2047;
                    else
                        flux_mem[gen_idx] <= sample_value[10:0];

                    if (gen_idx == N_SAMPLES-1) begin
                        state <= S_INIT_SEARCH;
                        period_samples <= MIN_PERIOD_SAMPLES;
                        duration_samples <= MIN_DURATION_SAMPLES;
                        scan_idx <= 0;
                    end else begin
                        gen_idx <= gen_idx + 1'b1;
                    end
                end

                S_INIT_SEARCH: begin
                    // Initialize sums for this candidate period and duration.
                    scan_idx <= 0;
                    transit_count <= 0;
                    transit_sum <= 0;
                    total_sum <= 0;
                    state <= S_SCAN;
                end

                S_SCAN: begin
                    // One sample processed per cycle. Phase is measured in samples.
                    // For integer period P, phase index = sample_index mod P.
                    phase_samples <= scan_idx % period_samples;
                    total_sum <= total_sum + flux_mem[scan_idx];

                    // Candidate window starts at each possible phase position.
                    // This implementation evaluates one candidate window per scan pass;
                    // win_start is advanced through phases in the SCORE/NEXT states.
                    if ((scan_idx % period_samples) >= win_start &&
                        (scan_idx % period_samples) < win_end) begin
                        transit_count <= transit_count + 1'b1;
                        transit_sum <= transit_sum + flux_mem[scan_idx];
                    end

                    if (scan_idx == N_SAMPLES-1) begin
                        state <= S_SCORE;
                    end else begin
                        scan_idx <= scan_idx + 1'b1;
                    end
                end

                S_SCORE: begin
                    // The mean-depth estimate is represented in flux integer units.
                    n_in <= transit_count;
                    n_out <= N_SAMPLES - transit_count;
                    sum_in <= transit_sum;
                    sum_out <= total_sum - transit_sum;

                    if ((transit_count >= 3) &&
                        ((N_SAMPLES - transit_count) >= 10) &&
                        (transit_count < N_SAMPLES)) begin
                        // Depth = mean(outside) - mean(inside), scaled integer.
                        mean_in_q <= transit_sum / transit_count;
                        mean_out_q <= (total_sum - transit_sum) /
                                      (N_SAMPLES - transit_count);
                        depth_tmp = ((total_sum - transit_sum) /
                                     (N_SAMPLES - transit_count)) -
                                    (transit_sum / transit_count);
                        depth_q <= depth_tmp;

                        if (depth_tmp > 0) begin
                            abs_depth <= depth_tmp;
                            depth_squared <= depth_tmp * depth_tmp;
                            score_temp <= (transit_count *
                                           (N_SAMPLES - transit_count) *
                                           depth_tmp * depth_tmp);
                            if ((transit_count *
                                 (N_SAMPLES - transit_count) *
                                 depth_tmp * depth_tmp) > best_score) begin
                                best_score <= transit_count *
                                              (N_SAMPLES - transit_count) *
                                              depth_tmp * depth_tmp;
                                best_period_samples <= period_samples;
                                best_duration_samples <= duration_samples;
                                best_depth_q <= depth_tmp;
                            end
                        end
                    end
                    state <= S_NEXT_DUR;
                end

                S_NEXT_DUR: begin
                    if (duration_samples + DURATION_STEP_SAMPLES <=
                        MAX_DURATION_SAMPLES) begin
                        duration_samples <= duration_samples +
                                            DURATION_STEP_SAMPLES;
                    end else begin
                        duration_samples <= MIN_DURATION_SAMPLES;
                        state <= S_NEXT_PER;
                    end
                    // Centered phase window. The first version starts at phase 0.
                    win_start <= 0;
                    win_end <= duration_samples;
                    scan_idx <= 0;
                    transit_count <= 0;
                    transit_sum <= 0;
                    total_sum <= 0;
                    if (duration_samples + DURATION_STEP_SAMPLES <=
                        MAX_DURATION_SAMPLES)
                        state <= S_INIT_SEARCH;
                end

                S_NEXT_PER: begin
                    if (period_samples < MAX_PERIOD_SAMPLES) begin
                        period_samples <= period_samples + 1'b1;
                        duration_samples <= MIN_DURATION_SAMPLES;
                        win_start <= 0;
                        win_end <= MIN_DURATION_SAMPLES;
                        state <= S_INIT_SEARCH;
                    end else begin
                        state <= S_FINISH;
                    end
                end

                S_FINISH: begin
                    busy <= 1'b0;
                    done <= 1'b1;
                    state <= S_IDLE;
                end

                default: state <= S_IDLE;
            endcase
        end
    end

endmodule
