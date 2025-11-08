defmodule Pythia.KernelsTest do
  use ExUnit.Case, async: true
  alias Pythia.Kernels

  describe "levenshtein/2" do
    test "returns 0 for identical strings" do
      assert Kernels.levenshtein("hello", "hello") == 0
      assert Kernels.levenshtein("", "") == 0
      assert Kernels.levenshtein("test", "test") == 0
    end

    test "returns length for empty string comparison" do
      assert Kernels.levenshtein("", "hello") == 5
      assert Kernels.levenshtein("hello", "") == 5
      assert Kernels.levenshtein("", "world") == 5
    end

    test "calculates distance for single character difference" do
      assert Kernels.levenshtein("cat", "bat") == 1
      assert Kernels.levenshtein("test", "best") == 1
      assert Kernels.levenshtein("hello", "hallo") == 1
    end

    test "calculates distance for classic examples" do
      assert Kernels.levenshtein("kitten", "sitting") == 3
      assert Kernels.levenshtein("saturday", "sunday") == 3
      assert Kernels.levenshtein("book", "back") == 2
    end

    test "handles unicode strings" do
      assert Kernels.levenshtein("café", "cafe") == 1
      assert Kernels.levenshtein("hello", "héllo") == 1
      assert Kernels.levenshtein("🎉🎊", "🎉") == 1
    end

    test "consistency with fallback implementation" do
      # Ensure NIF and fallback produce same results
      pairs = [
        {"kitten", "sitting"},
        {"saturday", "sunday"},
        {"", "hello"},
        {"test", "test"},
        {"abc", "xyz"},
        {"café", "cafe"}
      ]

      for {a, b} <- pairs do
        nif_result = Kernels.levenshtein(a, b)
        fallback_result = Pythia.KernelsFallback.levenshtein(a, b)
        assert nif_result == fallback_result,
               "Mismatch for #{inspect({a, b})}: NIF=#{nif_result}, Fallback=#{fallback_result}"
      end
    end

    test "guard clause rejects non-binary inputs" do
      # This should raise FunctionClauseError due to guard
      assert_raise FunctionClauseError, fn ->
        Kernels.levenshtein(123, "string")
      end

      assert_raise FunctionClauseError, fn ->
        Kernels.levenshtein("string", 456)
      end

      assert_raise FunctionClauseError, fn ->
        Kernels.levenshtein(nil, "string")
      end
    end

    test "handles moderately long strings" do
      str1 = String.duplicate("a", 100)
      str2 = String.duplicate("b", 100)
      assert Kernels.levenshtein(str1, str2) == 100
    end

    test "symmetric property" do
      assert Kernels.levenshtein("abc", "def") == Kernels.levenshtein("def", "abc")
      assert Kernels.levenshtein("hello", "world") == Kernels.levenshtein("world", "hello")
    end
  end
end
