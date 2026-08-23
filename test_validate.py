import sys
sys.path.insert(0, r"C:\Users\home\OneDrive\Documents\work\projects\ai voice calling agent\backend")

from domain_config_schema import validate_domain_config_file

config = validate_domain_config_file(
    r"C:\Users\home\OneDrive\Documents\work\projects\ai voice calling agent\domain-configs\absent-student.json"
)
print(f"✓ Validated: {config.domain_id} v{config.version}")
print(f"  Name: {config.name}")
print(f"  Steps: {len(config.question_flow)}")
print(f"  Extraction fields: {list(config.extraction_schema.keys())}")