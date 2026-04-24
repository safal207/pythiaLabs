defmodule Pythia.KernelsFallbackTest do
  use ExUnit.Case, async: true

  alias Pythia.KernelsFallback

  test "returns 0 for two empty strings" do
    assert KernelsFallback.levenshtein("", "") == 0
  end

  test "handles empty/filled strings symmetrically" do
    assert KernelsFallback.levenshtein("", "abc") == 3
    assert KernelsFallback.levenshtein("abc", "") == 3
  end

  test "matches classic levenshtein example" do
    assert KernelsFallback.levenshtein("kitten", "sitting") == 3
  end

  test "supports unicode graphemes" do
    assert KernelsFallback.levenshtein("привет", "привёт") == 1
  end
end
