import json
from pathlib import Path
from automation.data.generate_test_catalog import generate_catalog
from automation.utils.report_generator import generate

def main():
    cases = generate_catalog()
    Path('automation/tmp_shard').mkdir(exist_ok=True)
    payload = {
        'metadata': {'device': 'Android Emulator', 'android_version': '29'},
        'results': cases[:400]
    }
    (Path('automation/tmp_shard') / 'shard-0-results.json').write_text(json.dumps(payload))
    generate(Path('automation/tmp_shard'), Path('automation/mobile-report-pkg'))

if __name__ == '__main__':
    main()
