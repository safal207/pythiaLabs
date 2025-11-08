# Benchmark: Strategy Comparison
#
# Compares performance of different refinement strategies:
# - GreedyLCP: Fast, deterministic
# - RandomWalk: Exploratory
# - BeamSearch: Balanced
# - Adaptive (Multi-strategy): Dynamic selection
#
# Run: mix run benches/strategy_bench.exs

IO.puts("\n=== Pythia Strategy Benchmark ===\n")

test_cases = [
  # {source, target, description}
  {"kitten", "sitting", "Classic Levenshtein"},
  {"saturday", "sunday", "Moderate edits"},
  {"hello", "world", "Complete replacement"},
  {"", "python", "Empty to word"},
  {"elixir", "", "Word to empty"},
  {"abcdef", "fedcba", "Reversal"},
  {"test", "test", "Identical (trivial)"},
  {"programming", "programmer", "Suffix change"},
  {"The quick brown fox", "The slow brown dog", "Longer text"},
]

strategies = [
  {:greedy_only, "Greedy LCP (baseline)", enable_multi_strategy: false},
  {:adaptive, "Adaptive (Multi-strategy)", enable_multi_strategy: true},
  # Can't easily benchmark pure random/beam without modifying API
]

IO.puts("Test Cases: #{length(test_cases)}")
IO.puts("Strategies: #{length(strategies)}\n")

results = for {source, target, desc} <- test_cases do
  IO.puts("#{desc}: \"#{source}\" → \"#{target}\"")

  strategy_results = for {id, name, opts} <- strategies do
    {time, {:ok, result}} = :timer.tc(fn ->
      Pythia.refine(source, target, Keyword.merge([max_steps: 50], opts))
    end)

    steps = result.steps
    final_score = result.best.score
    converged = final_score == 0

    # Extract strategy switches from trace if multi-strategy
    strategy_switches = if opts[:enable_multi_strategy] do
      trace = result.trace
      strategies_used = trace
        |> Enum.map(&get_in(&1, [:meta, :strategy]))
        |> Enum.reject(&is_nil/1)
        |> Enum.uniq()

      switch_count = trace
        |> Enum.chunk_every(2, 1, :discard)
        |> Enum.count(fn [a, b] ->
          get_in(a, [:meta, :strategy]) != get_in(b, [:meta, :strategy])
        end)

      {length(strategies_used), switch_count}
    else
      {1, 0}
    end

    {strategies_used, switches} = strategy_switches

    IO.puts("  #{name}:")
    IO.puts("    Steps: #{steps}, Score: #{final_score}, " <>
            "Converged: #{converged}, Time: #{div(time, 1000)}ms")

    if opts[:enable_multi_strategy] do
      IO.puts("    Strategies used: #{strategies_used}, Switches: #{switches}")
    end

    %{
      strategy: id,
      steps: steps,
      score: final_score,
      converged: converged,
      time_us: time,
      strategies_used: strategies_used,
      switches: switches
    }
  end

  IO.puts("")

  %{
    test_case: desc,
    source: source,
    target: target,
    results: strategy_results
  }
end

# Summary statistics
IO.puts("\n=== Summary Statistics ===\n")

for {id, name, _opts} <- strategies do
  strategy_stats = results
    |> Enum.flat_map(& &1.results)
    |> Enum.filter(&(&1.strategy == id))

  total_steps = Enum.sum(Enum.map(strategy_stats, & &1.steps))
  avg_steps = Float.round(total_steps / length(strategy_stats), 2)

  converged_count = Enum.count(strategy_stats, & &1.converged)
  convergence_rate = Float.round(converged_count / length(strategy_stats) * 100, 1)

  total_time = Enum.sum(Enum.map(strategy_stats, & &1.time_us))
  avg_time = div(total_time, length(strategy_stats))

  IO.puts("#{name}:")
  IO.puts("  Avg steps: #{avg_steps}")
  IO.puts("  Convergence: #{converged_count}/#{length(strategy_stats)} (#{convergence_rate}%)")
  IO.puts("  Avg time: #{div(avg_time, 1000)}ms")

  if id == :adaptive do
    avg_strategies = strategy_stats
      |> Enum.map(& &1.strategies_used)
      |> Enum.sum()
      |> Kernel./(length(strategy_stats))
      |> Float.round(2)

    avg_switches = strategy_stats
      |> Enum.map(& &1.switches)
      |> Enum.sum()
      |> Kernel./(length(strategy_stats))
      |> Float.round(2)

    IO.puts("  Avg strategies per run: #{avg_strategies}")
    IO.puts("  Avg strategy switches: #{avg_switches}")
  end

  IO.puts("")
end

IO.puts("=== Benchmark Complete ===\n")
