defmodule Pythia.PlannerTest do
  use ExUnit.Case, async: true

  alias Pythia.{Critic, Executor, Planner}

  test "stops when threshold is reached" do
    planner = Planner.new("kitten", "sitting", max_steps: 30, threshold: 0, no_improve_limit: 8)

    assert {:ok, %{best: %{score: 0}, steps: steps, trace: trace}} =
             Planner.run(planner, Executor.new(), Critic.new())

    assert steps > 0
    assert length(trace) == steps
  end

  test "respects max_steps guard" do
    planner = Planner.new("abc", "xyz", max_steps: 1, threshold: -1, no_improve_limit: 8)

    assert {:ok, %{steps: 1, trace: [_]}} = Planner.run(planner, Executor.new(), Critic.new())
  end

  test "stops by no_improve_limit when objective cannot improve" do
    planner = Planner.new("abc", "abc", max_steps: 50, threshold: -1, no_improve_limit: 3)

    assert {:ok, %{steps: 3, trace: trace}} = Planner.run(planner, Executor.new(), Critic.new())

    assert Enum.all?(trace, fn step -> step.score == 0 end)
  end
end
