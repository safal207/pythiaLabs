defmodule Pythia.Critic do
  @moduledoc """
  Critic module that analyzes reasoning traces and provides advice.

  v0.1 Implementation: Simple heuristics-based advisor without LLM.
  - Detects score plateau (no improvement over N steps)
  - Detects repetitive patterns (loops in trace)
  - Suggests interventions (random mutation, strategy shift, early stop)

  Future: LLM integration for confidence-based analysis and hypothesis generation.
  """

  defstruct []

  def new, do: %__MODULE__{}

  @doc """
  Analyzes current state and trace, returns advice.

  Returns one of:
  - :noop - No intervention needed
  - {:suggest_random_mutation} - Try random change to break plateau
  - {:suggest_strategy_shift} - Switch to different proposal strategy
  - {:suggest_early_stop} - Stop refinement (good enough or stuck)
  """
  def advise(_state, trace) do
    cond do
      # Not enough data to analyze
      length(trace) < 3 ->
        :noop

      # Check for score plateau (last 3 steps have same score)
      detect_plateau?(trace, window: 3) ->
        {:suggest_random_mutation, reason: "Score plateau detected"}

      # Check for repetitive candidates (looping)
      detect_loop?(trace, window: 5) ->
        {:suggest_strategy_shift, reason: "Candidate loop detected"}

      # Check if making very slow progress
      detect_slow_progress?(trace, window: 5, threshold: 0.1) ->
        {:suggest_random_mutation, reason: "Slow progress detected"}

      # Default: no intervention
      true ->
        :noop
    end
  end

  @doc """
  Checks if intervention should be applied based on advice and current conditions.
  """
  def should_intervene?(advice) do
    case advice do
      :noop -> false
      {:suggest_random_mutation, _} -> true
      {:suggest_strategy_shift, _} -> true
      {:suggest_early_stop, _} -> true
      _ -> false
    end
  end

  # Private helpers

  defp detect_plateau?(trace, opts) do
    window = Keyword.get(opts, :window, 3)

    if length(trace) < window do
      false
    else
      recent_scores = trace
        |> Enum.take(window)
        |> Enum.map(& &1.score)

      # All scores in window are identical
      recent_scores |> Enum.uniq() |> length() == 1
    end
  end

  defp detect_loop?(trace, opts) do
    window = Keyword.get(opts, :window, 5)

    if length(trace) < window do
      false
    else
      recent_candidates = trace
        |> Enum.take(window)
        |> Enum.map(& &1.candidate)

      # Check if we've seen same candidate multiple times in window
      unique_count = recent_candidates |> Enum.uniq() |> length()
      unique_count < length(recent_candidates) - 1
    end
  end

  defp detect_slow_progress?(trace, opts) do
    window = Keyword.get(opts, :window, 5)
    threshold = Keyword.get(opts, :threshold, 0.1)

    if length(trace) < window do
      false
    else
      recent_scores = trace
        |> Enum.take(window)
        |> Enum.map(& &1.score)
        |> Enum.filter(&is_number/1)

      if length(recent_scores) < 2 do
        false
      else
        first_score = List.last(recent_scores)
        last_score = hd(recent_scores)

        # If improvement is less than threshold over window
        improvement = first_score - last_score
        improvement < threshold and improvement >= 0
      end
    end
  end
end
