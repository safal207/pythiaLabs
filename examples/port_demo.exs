port_path = Path.expand("workers/solver_port/target/release/solver_port", File.cwd!())
port = Port.open({:spawn_executable, port_path}, [:binary, args: [], packet: 4])

req = %{
  grid: [
    [0,0,0,1,0,0,0],
    [1,1,0,1,0,1,0],
    [0,0,0,0,0,1,0],
    [0,1,1,1,0,0,0],
    [0,0,0,0,1,1,0]
  ],
  start: {0,0},
  goal: {4,6}
}

bin = Jason.encode!(req)
Port.command(port, bin)
receive do
  {^port, {:data, resp}} ->
    case Jason.decode(resp) do
      {:ok, %{"length" => len}} -> IO.puts("Maze path length: #{inspect(len)}")
      other -> IO.inspect(other, label: :unexpected)
    end
after
  5_000 -> IO.puts("Timeout from worker")
end
