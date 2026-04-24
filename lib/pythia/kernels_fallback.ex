defmodule Pythia.KernelsFallback do
  @moduledoc "Pure Elixir fallback (slower)."
  def levenshtein(a, b), do: do_lev(String.graphemes(a), String.graphemes(b))

  defp do_lev([], ys), do: length(ys)
  defp do_lev(xs, []), do: length(xs)

  defp do_lev(xs, ys) do
    m = length(xs)
    n = length(ys)
    row0 = Enum.to_list(0..n)

    Enum.with_index(xs, 1)
    |> Enum.reduce(row0, fn {xi, i}, prev_row ->
      Enum.with_index(ys, 1)
      |> Enum.reduce([i], fn {yj, j}, acc ->
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
