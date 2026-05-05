.PHONY: demo demo-clean

demo:
	mix run examples/paid_review_demo.exs

demo-clean:
	rm -f examples/output/paid_review_demo_artifact.json
