Code.require_file("mix/tasks/compile.rustler_fallback.ex", __DIR__)

defmodule Pythia.MixProject do
  use Mix.Project

  def project do
    [
      app: :liminal_pythia,
      version: "0.1.0",
      elixir: "~> 1.15",
      start_permanent: Mix.env() == :prod,
      compilers: compilers(),
      deps: deps()
    ]
  end

  def application do
    [extra_applications: [:logger]]
  end

  defp deps do
    [
      {:rustler, "~> 0.33"},
      {:jason, "~> 1.4"},
      {:telemetry, "~> 1.2"},
      {:stream_data, "~> 1.0", only: :test}
    ]
  end

  defp compilers do
    [:rustler_fallback | Mix.compilers()]
  end
end
