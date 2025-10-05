alias Pythia.Kernels

pairs = for _ <- 1..200, do: {"kitten" <> :crypto.strong_rand_bytes(4) |> Base.encode16(), "sitting"}

{t1, _} = :timer.tc(fn -> Enum.each(pairs, fn {a,b} -> Pythia.KernelsFallback.levenshtein(a,b) end) end)
{t2, _} = :timer.tc(fn -> Enum.each(pairs, fn {a,b} -> Kernels.levenshtein(a,b) end) end)

IO.puts("Fallback (Elixir): #{div(t1,1000)} ms for #{length(pairs)} pairs")
IO.puts("NIF (Rust)    : #{div(t2,1000)} ms for #{length(pairs)} pairs")
