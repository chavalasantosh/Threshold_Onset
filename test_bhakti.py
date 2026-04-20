from model.santok_engine import SantokEngine
import os

print("=" * 65)
print("TESTING NATIVE GENERALIZATION (Bhakti Yoga Corpus)")
print("=================================================================")

# Load the new Bhakti Yoga dataset
json_path = os.path.join("output", "bhakti_yoga_vivekananda_santok_unified.json")
engine = SantokEngine(json_path)

print(f"[*] Engine successfully mapped new corpus.")
print(f"[*] Extracting 5 distinct structural sequences blindly:\n")

for i in range(1, 6):
    print(f"--- RUN {i} ---")
    output = engine.generate(length=25)
    print(output)
    print()
