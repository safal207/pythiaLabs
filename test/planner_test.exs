defmodule Pythia.PlannerTest do
  use ExUnit.Case, async: true

  alias Pythia.{Critic, Executor, Planner}

  test "stops when threshold is reached" do
    planner = Planner.new("kitten", "sitting", max_steps: 30, threshold: 0, no_improve_limit: 8)

    assert {:ok, %{best: %{score: 0}, steps: steps, stop_reason: :threshold, trace: trace}} =
             Planner.run(planner, Executor.new(), Critic.new())

    assert steps > 0
    assert length(trace) == steps
  end

  test "respects max_steps guard" do
    planner = Planner.new("abc", "xyz", max_steps: 1, threshold: -1, no_improve_limit: 8)

    assert {:ok, %{steps: 1, stop_reason: :max_steps, trace: [_]}} =
             Planner.run(planner, Executor.new(), Critic.new())
  end

  test "stops by no_improve_limit when objective cannot improve" do
    planner = Planner.new("abc", "abc", max_steps: 50, threshold: -1, no_improve_limit: 3)

    assert {:ok, %{steps: 3, stop_reason: :no_improve_limit, trace: trace}} =
             Planner.run(planner, Executor.new(), Critic.new())

    assert Enum.all?(trace, fn step -> step.score == 0 end)
  end

  test "emits telemetry events for step and stop" do
    test_pid = self()
    ref = make_ref()

    :telemetry.attach_many(
      "planner-test-#{inspect(ref)}",
      [[:pythia, :planner, :step], [:pythia, :planner, :stop]],
      fn event, measurements, metadata, _ ->
        send(test_pid, {:event, event, measurements, metadata})
      end,
      nil
    )

    planner =
      Planner.new("abc", "abc", max_steps: 3, threshold: -1, no_improve_limit: 2, trace_id: 42)

    assert {:ok, _} = Planner.run(planner, Executor.new(), Critic.new())

    assert_receive {:event, [:pythia, :planner, :step], %{step: 1, score: 0}, %{trace_id: 42}},
                   500

    assert_receive {:event, [:pythia, :planner, :stop], %{steps: 2},
                    %{trace_id: 42, stop_reason: :no_improve_limit}},
                   500

    :telemetry.detach("planner-test-#{inspect(ref)}")
  end
end
