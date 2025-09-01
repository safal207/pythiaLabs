defmodule Pythia.MixProject do
  use Mix.Project

  def project do
    [
      app: :liminal_pythia,
      version: "0.1.0",
      elixir: "~> 1.15",
      start_permanent: Mix.env() == :prod,
      compilers: [:rustler] ++ Mix.compilers(),
      deps: deps()
    ]
  end

  def application do
    [extra_applications: [:logger]]
  end

  defp deps do
    [
      {:rustler, "~> 0.33"},
      {:jason, "~> 1.4"}
    ]
  end
end
