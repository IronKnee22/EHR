import json

import pandas as pd

with open(r"data/ehr.school.v0.json", "r", encoding="utf-8") as file:
    web_template = json.load(file)


def extract_fillable_fields(node, path=""):
    fields = []
    current_path = path + node.get("aqlPath", "")
    if "inputs" in node and node.get("rmType") not in {"CODE_PHRASE", "PARTY_PROXY"}:
        fields.append(
            {
                "label": node.get("name"),
                "id": node.get("id"),
                "rmType": node.get("rmType"),
                "aqlPath": current_path,
                "inputType": [inp.get("type") for inp in node.get("inputs", [])],
            }
        )
    for child in node.get("children", []):
        fields.extend(extract_fillable_fields(child, current_path))
    return fields


fillable_fields = extract_fillable_fields(web_template["tree"])


with open(r"data/entrys.txt", "w", encoding="utf-8") as output_file:
    json.dump(fillable_fields, output_file, ensure_ascii=False, indent=2)


df_fillable = pd.DataFrame(fillable_fields)
print(df_fillable.head())
