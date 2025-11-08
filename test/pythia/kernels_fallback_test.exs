defmodule Pythia.KernelsFallbackTest do
  use ExUnit.Case, async: true
  alias Pythia.KernelsFallback

  describe "levenshtein/2" do
    test "returns 0 for identical strings" do
      assert KernelsFallback.levenshtein("hello", "hello") == 0
      assert KernelsFallback.levenshtein("", "") == 0
      assert KernelsFallback.levenshtein("a", "a") == 0
    end

    test "returns length for empty string comparison" do
      assert KernelsFallback.levenshtein("", "hello") == 5
      assert KernelsFallback.levenshtein("hello", "") == 5
      assert KernelsFallback.levenshtein("", "a") == 1
      assert KernelsFallback.levenshtein("a", "") == 1
    end

    test "calculates distance for single character difference" do
      assert KernelsFallback.levenshtein("cat", "bat") == 1
      assert KernelsFallback.levenshtein("hello", "helo") == 1
      assert KernelsFallback.levenshtein("kitten", "sitten") == 1
    end

    test "calculates distance for classic examples" do
      # kitten → sitten → sittin → sitting (3 edits)
      assert KernelsFallback.levenshtein("kitten", "sitting") == 3

      # saturday → sunday (3 edits: remove a, remove t, remove r)
      assert KernelsFallback.levenshtein("saturday", "sunday") == 3
    end

    test "handles unicode correctly" do
      assert KernelsFallback.levenshtein("café", "cafe") == 1
      assert KernelsFallback.levenshtein("🎉", "🎊") == 1
      assert KernelsFallback.levenshtein("hello", "héllo") == 1
    end

    test "handles longer strings" do
      str1 = "The quick brown fox jumps over the lazy dog"
      str2 = "The quick brown fox jumped over the lazy dog"
      assert KernelsFallback.levenshtein(str1, str2) == 2
    end

    test "symmetric property" do
      # distance(a,b) == distance(b,a)
      assert KernelsFallback.levenshtein("abc", "def") ==
             KernelsFallback.levenshtein("def", "abc")

      assert KernelsFallback.levenshtein("kitten", "sitting") ==
             KernelsFallback.levenshtein("sitting", "kitten")
    end

    test "triangle inequality" do
      # distance(a,c) <= distance(a,b) + distance(b,c)
      d_ac = KernelsFallback.levenshtein("abc", "xyz")
      d_ab = KernelsFallback.levenshtein("abc", "def")
      d_bc = KernelsFallback.levenshtein("def", "xyz")

      assert d_ac <= d_ab + d_bc
    end

    test "non-negative property" do
      assert KernelsFallback.levenshtein("any", "string") >= 0
      assert KernelsFallback.levenshtein("", "") >= 0
    end
  end
end
