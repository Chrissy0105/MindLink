from app import app

print("🔍 ALL AVAILABLE ENDPOINTS:")
print("=" * 60)
for rule in app.url_map.iter_rules():
    if 'static' not in rule.rule:
        methods = ', '.join(sorted([m for m in rule.methods if m not in ['OPTIONS', 'HEAD']]))
        print(f"📍 {rule.rule:35} [Methods: {methods}]")
