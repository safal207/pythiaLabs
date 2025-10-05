defmodule Pythia.KernelsFallback do
  @moduledoc "Pure Elixir fallback (slower)."
  def levenshtein(a, b), do: do_lev(String.graphemes(a), String.graphemes(b))

  defp do_lev(xs, ys) do
    m = length(xs)
    n = length(ys)
    row0 = Enum.to_list(0..n)
    Enum.reduce(1..m, row0, fn i, prev_row ->
      xi = Enum.at(xs, i - 1)
      Enum.reduce(1..n, [i], fn j, acc ->
        yj = Enum.at(ys, j - 1)
        cost = if xi == yj, do: 0, else: 1
        insert = hd(acc) + 1
        delete = Enum.at(prev_row, j) + 1
        replace = Enum.at(prev_row, j - 1) + cost
        [Enum.min([insert, delete, replace]) | acc]
      end)
      |> Enum.reverse()
    end)
    |> List.last()
  end
end
