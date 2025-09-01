defmodule Pythia.Critic do
  @moduledoc "Critic hook placeholder (plug GPT‑5 here later)."
  defstruct []
  def new, do: %__MODULE__{}
  def advise(_state, _trace), do: :noop
end
