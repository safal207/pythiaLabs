alias Pythia

source = System.get_env("LEV_SRC", "kitten")
 target = System.get_env("LEV_TGT", "sitting")

{:ok, result} = Pythia.refine(source, target, max_steps: 30, threshold: 0, no_improve_limit: 8)

IO.puts("\n== Levenshtein demo ==")
IO.inspect(result.best, label: "best")
IO.puts("steps: #{result.steps}")
IO.puts("trace:")
for t <- result.trace, do: IO.puts("  step=#{t.step} op=#{inspect(t.proposal)} candidate=\"#{t.candidate}\" score=#{t.score}")
