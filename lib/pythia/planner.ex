defmodule Pythia.Planner do
  @moduledoc "HRM-like outer loop: propose → run → measure → refine (string demo)."
  require Logger
  alias Pythia.Executor

  defstruct problem: nil,
            objective: nil,
            state: nil,
            best: nil,
            step: 0,
            max_steps: 20,
            threshold: 0,
            no_improve_limit: 5,
            no_improve: 0,
            trace_id: nil,
            trace: []

  def new(problem, objective, opts) do
    %__MODULE__{
      problem: problem,
      objective: objective,
      state: %{candidate: problem},
      best: %{candidate: problem, score: :infinity},
      max_steps: Keyword.get(opts, :max_steps, 20),
      threshold: Keyword.get(opts, :threshold, 0),
      no_improve_limit: Keyword.get(opts, :no_improve_limit, 5),
      trace_id: Keyword.get(opts, :trace_id, System.unique_integer([:positive, :monotonic]))
    }
  end

  def run(%__MODULE__{} = p, %Executor{} = exec, critic) do
    do_run(p, exec, critic)
  end

  defp do_run(%__MODULE__{step: s, max_steps: m} = p, _e, _c) when s >= m do
    finalize(p, :max_steps)
  end

  defp do_run(p, exec, critic) do
    proposal = propose(p.state.candidate, p.objective)
    {new_candidate, meta} = Executor.apply_proposal(exec, p.state.candidate, proposal)
    score = Executor.score(exec, new_candidate, p.objective)

    {best, no_improve} =
      case p.best do
        %{score: s} when is_number(s) and score < s ->
          {%{candidate: new_candidate, score: score}, 0}

        %{score: :infinity} ->
          {%{candidate: new_candidate, score: score}, 0}

        _ ->
          {p.best, p.no_improve + 1}
      end

    step = p.step + 1

    trace_entry = %{
      step: step,
      proposal: proposal,
      candidate: new_candidate,
      score: score,
      meta: meta
    }

    p = %{
      p
      | state: %{candidate: new_candidate},
        best: best,
        step: step,
        no_improve: no_improve,
        trace: [trace_entry | p.trace]
    }

    :telemetry.execute(
      [:pythia, :planner, :step],
      %{step: step, score: score},
      %{trace_id: p.trace_id, proposal: proposal, op: meta.op}
    )

    Logger.info(
      "pythia_step trace_id=#{p.trace_id} step=#{step} op=#{meta.op} score=#{score} no_improve=#{no_improve}"
    )

    cond do
      score <= p.threshold ->
        finalize(p, :threshold)

      no_improve >= p.no_improve_limit ->
        _ = critic
        finalize(p, :no_improve_limit)

      true ->
        do_run(p, exec, critic)
    end
  end

  defp finalize(p, stop_reason) do
    :telemetry.execute(
      [:pythia, :planner, :stop],
      %{steps: p.step},
      %{trace_id: p.trace_id, stop_reason: stop_reason, best_score: p.best.score}
    )

    Logger.info("pythia_stop trace_id=#{p.trace_id} steps=#{p.step} reason=#{stop_reason}")
    {:ok, %{best: p.best, steps: p.step, stop_reason: stop_reason, trace: Enum.reverse(p.trace)}}
  end

  defp propose(current, target) do
    {prefix, c_rest, t_rest} = longest_common_prefix(current, target)

    cond do
      c_rest == "" and t_rest == "" -> {:noop}
      c_rest == "" -> {:insert, String.first(t_rest), String.length(prefix)}
      t_rest == "" -> {:delete, String.length(prefix)}
      true -> {:replace, String.first(t_rest), String.length(prefix)}
    end
  end

  defp longest_common_prefix(a, b), do: lcp(a, b, "")
  defp lcp(<<>>, rest, acc), do: {acc, "", rest}
  defp lcp(rest, <<>>, acc), do: {acc, rest, ""}

  defp lcp(<<x::utf8, xs::binary>>, <<y::utf8, ys::binary>>, acc) when x == y,
    do: lcp(xs, ys, acc <> <<x::utf8>>)

  defp lcp(xs, ys, acc), do: {acc, xs, ys}
end
