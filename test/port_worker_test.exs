defmodule Pythia.PortWorkerTest do
  use ExUnit.Case, async: false

  @worker_dir Path.expand("../workers/solver_port", __DIR__)
  @binary Path.join([@worker_dir, "target", "release", "solver_port"])

  setup_all do
    cond do
      File.exists?(@binary) ->
        :ok

      cargo = System.find_executable("cargo") ->
        {output, code} =
          System.cmd(cargo, ["build", "--release"],
            cd: @worker_dir,
            stderr_to_stdout: true
          )

        if code != 0 do
          raise "cargo build failed with exit #{code}:\n#{output}"
        end

        unless File.exists?(@binary) do
          raise "cargo build succeeded but binary not found at #{@binary}"
        end

        :ok

      true ->
        :ok
    end
  end

  defp open_worker do
    cond do
      File.exists?(@binary) ->
        Port.open({:spawn_executable, @binary}, [:binary, args: [], packet: 4])

      is_nil(System.find_executable("cargo")) ->
        {:error, :no_cargo}

      true ->
        ExUnit.Assertions.flunk(
          "solver_port binary missing at #{@binary} despite cargo being available"
        )
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
      {:error, :no_cargo} ->
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
      {:error, :no_cargo} ->
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
      {:error, :no_cargo} ->
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
