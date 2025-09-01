defmodule Pythia do
  @moduledoc "Public API for liminal-pythia MVP."
  alias Pythia.{Planner, Executor, Critic}

  @type options :: [max_steps: pos_integer(), threshold: number(), no_improve_limit: pos_integer()]

  def refine(problem, objective, opts \\ []) do
    planner = Planner.new(problem, objective, opts)
    exec = Executor.new()
    critic = Critic.new()
    Planner.run(planner, exec, critic)
  end
end
