defmodule Pythia.PortWorkerTest do
  use ExUnit.Case, async: false

  @worker_dir Path.expand("../workers/solver_port", __DIR__)
  @binary Path.join([@worker_dir, "target", "release", "solver_port"])

  setup_all do
    unless File.exists?(@binary) do
      case System.find_executable("cargo") do
        nil ->
          :ok

        cargo ->
          {_, 0} =
            System.cmd(cargo, ["build", "--release"],
              cd: @worker_dir,
              stderr_to_stdout: true
            )
      end
    end

    :ok
  end

  defp open_worker do
    if File.exists?(@binary) do
      Port.open({:spawn_executable, @binary}, [:binary, args: [], packet: 4])
    else
      {:error, :binary_missing}
    end
  end

  defp request(port, payload, timeout \\ 5_000) do
    true = Port.command(port, Jason.encode!(payload))

    receive do
      {^port, {:data, data}} -> Jason.decode!(data)
    after
      timeout -> :timeout
    end
  end

  test "packet:4 round-trip returns shortest path length" do
    case open_worker() do
      {:error, :binary_missing} ->
        IO.puts(:stderr, "[port_worker_test] binary missing, skipping")

      port ->
        try do
          resp =
            request(port, %{
              grid: [
                [0, 0, 0, 1, 0, 0, 0],
                [1, 1, 0, 1, 0, 1, 0],
                [0, 0, 0, 0, 0, 1, 0],
                [0, 1, 1, 1, 0, 0, 0],
                [0, 0, 0, 0, 1, 1, 0]
              ],
              start: [0, 0],
              goal: [4, 6]
            })

          assert is_integer(resp["length"])
          assert resp["length"] > 0
        after
          Port.close(port)
        end
    end
  end

  test "worker reports validation error for malformed grid" do
    case open_worker() do
      {:error, :binary_missing} ->
        IO.puts(:stderr, "[port_worker_test] binary missing, skipping")

      port ->
        try do
          resp =
            request(port, %{
              grid: [[0, 0], [0]],
              start: [0, 0],
              goal: [1, 0]
            })

          assert resp["length"] == nil
          assert is_binary(resp["error"])
        after
          Port.close(port)
        end
    end
  end

  test "worker handles multiple frames on the same port" do
    case open_worker() do
      {:error, :binary_missing} ->
        IO.puts(:stderr, "[port_worker_test] binary missing, skipping")

      port ->
        try do
          resp1 =
            request(port, %{
              grid: [[0, 0, 0], [1, 1, 0], [0, 0, 0]],
              start: [0, 0],
              goal: [2, 2]
            })

          assert resp1["length"] == 4

          resp2 =
            request(port, %{
              grid: [[0, 0], [0, 0]],
              start: [0, 0],
              goal: [1, 1]
            })

          assert resp2["length"] == 2
        after
          Port.close(port)
        end
    end
  end
end
