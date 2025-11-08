# Multi-Strategy Demonstration
#
# This demo shows how Pythia dynamically switches between strategies
# based on progress and Critic advice.
#
# Run: mix run examples/multi_strategy_demo.exs

IO.puts("\n=== Pythia Multi-Strategy Demo ===\n")

source = System.get_env("SOURCE", "programming")
target = System.get_env("TARGET", "programmer")

IO.puts("Refining: \"#{source}\" → \"#{target}\"\n")

# Run with multi-strategy enabled
IO.puts("🔄 Running with ADAPTIVE strategy selection...\n")

{time, {:ok, result}} = :timer.tc(fn ->
  Pythia.refine(source, target,
    max_steps: 30,
    enable_multi_strategy: true,
    strategy_opts: [
      default_strategy: :greedy_lcp,
      enable_adaptive: true
    ]
  )
end)

IO.puts("✅ Result:")
IO.puts("  Best: \"#{result.best.candidate}\"")
IO.puts("  Score: #{result.best.score}")
IO.puts("  Steps: #{result.steps}")
IO.puts("  Time: #{div(time, 1000)}ms\n")

# Analyze strategy usage
IO.puts("📊 Strategy Analysis:\n")

strategies_used = result.trace
  |> Enum.map(&get_in(&1, [:meta, :strategy]))
  |> Enum.reject(&is_nil/1)

strategy_counts = strategies_used
  |> Enum.frequencies()
  |> Enum.sort_by(fn {_, count} -> -count end)

IO.puts("  Strategies used:")
for {strategy, count} <- strategy_counts do
  percentage = Float.round(count / length(strategies_used) * 100, 1)
  IO.puts("    #{strategy}: #{count} steps (#{percentage}%)")
end

# Find strategy switches
switches = result.trace
  |> Enum.chunk_every(2, 1, :discard)
  |> Enum.filter(fn [a, b] ->
    get_in(a, [:meta, :strategy]) != get_in(b, [:meta, :strategy])
  end)

IO.puts("\n  Strategy switches: #{length(switches)}")

if length(switches) > 0 do
  IO.puts("\n  Switch points:")
  for [prev, curr] <- switches do
    prev_strategy = get_in(prev, [:meta, :strategy])
    curr_strategy = get_in(curr, [:meta, :strategy])
    step = curr.step
    reason = case get_in(curr, [:meta, :critic_advice]) do
      {:suggest_random_mutation, r} -> "#{r[:reason]}"
      {:suggest_strategy_shift, r} -> "#{r[:reason]}"
      _ -> "adaptive"
    end

    IO.puts("    Step #{step}: #{prev_strategy} → #{curr_strategy} (#{reason})")
  end
end

# Show detailed trace
IO.puts("\n📝 Detailed Trace:\n")

for entry <- Enum.take(result.trace, 15) do
  strategy = get_in(entry, [:meta, :strategy]) || :unknown
  advice = case get_in(entry, [:meta, :critic_advice]) do
    :noop -> ""
    {:suggest_random_mutation, _} -> " 🎲"
    {:suggest_strategy_shift, _} -> " 🔀"
    {:suggest_early_stop, _} -> " 🛑"
    _ -> ""
  end

  IO.puts("  #{entry.step}. [#{strategy}#{advice}] \"#{entry.candidate}\" (score: #{entry.score})")
end

if result.steps > 15 do
  IO.puts("  ... (#{result.steps - 15} more steps)")
end

# Compare with greedy-only
IO.puts("\n🔁 Comparing with GREEDY-ONLY strategy...\n")

{time_greedy, {:ok, result_greedy}} = :timer.tc(fn ->
  Pythia.refine(source, target,
    max_steps: 30,
    enable_multi_strategy: false
  )
end)

IO.puts("✅ Greedy Result:")
IO.puts("  Best: \"#{result_greedy.best.candidate}\"")
IO.puts("  Score: #{result_greedy.best.score}")
IO.puts("  Steps: #{result_greedy.steps}")
IO.puts("  Time: #{div(time_greedy, 1000)}ms\n")

# Comparison
IO.puts("📈 Comparison:\n")

if result.best.score <= result_greedy.best.score do
  improvement = result_greedy.best.score - result.best.score
  IO.puts("  ✨ Adaptive achieved BETTER score (Δ: #{improvement})")
else
  IO.puts("  ⚠️  Greedy achieved better score")
end

step_diff = result.steps - result_greedy.steps
if step_diff < 0 do
  IO.puts("  ⚡ Adaptive used #{-step_diff} FEWER steps")
elsif step_diff > 0 do
  IO.puts("  ⚠️  Adaptive used #{step_diff} more steps")
else
  IO.puts("  ➡️  Same number of steps")
end

time_diff = time - time_greedy
if time_diff < 0 do
  IO.puts("  ⚡ Adaptive was #{div(-time_diff, 1000)}ms faster")
else
  IO.puts("  ⏱️  Adaptive took #{div(time_diff, 1000)}ms longer (overhead from strategy selection)")
end

IO.puts("\n=== Demo Complete ===\n")

IO.puts("💡 Try with different strings:")
IO.puts("  SOURCE=\"hello\" TARGET=\"world\" mix run examples/multi_strategy_demo.exs")
IO.puts("  SOURCE=\"kitten\" TARGET=\"sitting\" mix run examples/multi_strategy_demo.exs\n")
