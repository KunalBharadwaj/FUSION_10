import os, re
for f in ['test_use_cases.py', 'test_business_rules.py', 'test_workflows.py']:
    path = os.path.join(r"c:\Users\ratan\OneDrive\Desktop\assi 4B_G2\Fusion\FusionIIIT\applications\hr2\tests", f)
    with open(path, 'r', encoding='utf-8', errors='ignore') as file:
        content = file.read()
    content = re.sub(r'[^\x00-\x7F]+', '', content)
    with open(path, 'w', encoding='utf-8') as file:
        file.write(content)
