import json
from agents.orchestrator import NL2SQLOrchestrator

def run_evaluation():
    with open("evaluation/dataset.json", encoding="utf-8") as f:
        dataset = json.load(f)

    pipeline = NL2SQLOrchestrator()
    passed = 0

    for i, item in enumerate(dataset, 1):
        print("=" * 60)
        print("TEST", i)
        print(item["question"])

        try:
            result = pipeline.run(item["question"])
            retrieved = {x["table"] for x in result["retrieved"]}
            expected = set(item["expected_tables"])
            score = len(retrieved & expected) / len(expected)

            print("SQL:", result["sql"])
            print("Retrieved:", retrieved)
            print("Expected:", expected)
            print("Retrieval score:", f"{score:.2%}")

            if score >= 0.5:
                passed += 1
        except Exception as exc:
            print("FAILED:", exc)

    print("=" * 60)
    print(f"Passed: {passed}/{len(dataset)}")

if __name__ == "__main__":
    run_evaluation()
