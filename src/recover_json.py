import re
import json

INPUT = "data/fake_property_data_new.json"
OUTPUT = "data/recovered_objects.jsonl"

def recover_objects(text):
    # Find all objects { ... }
    pattern = r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}'
    return re.findall(pattern, text)

if __name__ == "__main__":
    raw = open(INPUT, "r", encoding="utf8", errors="ignore").read()

    objs = recover_objects(raw)

    print(f"Found possible objects: {len(objs)}")

    out = open(OUTPUT, "w", encoding="utf8")

    count = 0
    for obj in objs:
        try:
            fixed = obj.replace("'", '"')
            fixed = re.sub(r'(?<=\d)\s+sqft[s]?', '', fixed)
            o = json.loads(fixed)
            out.write(json.dumps(o) + "\n")
            count += 1
        except:
            pass

    print(f"Valid JSON objects recovered: {count}")
    print(f"Saved to {OUTPUT}")
