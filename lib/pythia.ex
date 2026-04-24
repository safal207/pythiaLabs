defmodule Pythia do
  @moduledoc "Public API for liminal-pythia MVP."
  alias Pythia.{Planner, Executor, Critic}

  @type options :: [
          max_steps: pos_integer(),
          threshold: number(),
          no_improve_limit: pos_integer(),
          trace_id: integer()
        ]
  @type refine_v1_request :: %{
          required(:source) => String.t(),
          required(:target) => String.t(),
          optional(:options) => options()
        }
  @type refine_v1_response :: %{
          version: String.t(),
          source: String.t(),
          target: String.t(),
          steps: non_neg_integer(),
          stop_reason: atom(),
          best: %{candidate: String.t(), score: non_neg_integer()},
          trace: list(map())
        }

  def refine(problem, objective, opts \\ []) do
    planner = Planner.new(problem, objective, opts)
    exec = Executor.new()
    critic = Critic.new()
    Planner.run(planner, exec, critic)
  end

  @spec refine_v1(refine_v1_request()) :: {:ok, refine_v1_response()} | {:error, atom()}
  def refine_v1(%{source: source, target: target} = req)
      when is_binary(source) and is_binary(target) do
    opts = Map.get(req, :options, [])

    with {:ok, result} <- refine(source, target, opts) do
      {:ok,
       %{
         version: "v1",
         source: source,
         target: target,
         steps: result.steps,
         stop_reason: result.stop_reason,
         best: result.best,
         trace: result.trace
       }}
    end
  end

  def refine_v1(_), do: {:error, :invalid_request}
end
