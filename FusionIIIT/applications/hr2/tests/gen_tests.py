import yaml
import os

base_path = r"c:\Users\ratan\OneDrive\Desktop\assi 4B_G2\Fusion\FusionIIIT\applications\hr2\tests"

def sanitize(name):
    return "".join(c for c in name if c.isalnum() or c == '_').rstrip()

def generate_uc():
    with open(os.path.join(base_path, "specs", "use_cases.yaml"), "r") as f:
        data = yaml.safe_load(f)
    
    code = "from .conftest import UCTestBase\n\n"
    for uc in data.get("use_cases", []):
        cls_name = f"Test{sanitize(uc['id'].replace('-',''))}_{sanitize(uc['title'].replace(' ', ''))}"
        code += f"class {cls_name}(UCTestBase):\n"
        code += f"    \"\"\"{uc['id']}: {uc['title']}\"\"\"\n\n"
        
        for i, hp in enumerate(uc.get("happy_paths", [])):
            code += f"    def test_hp{i+1}_{sanitize(hp['scenario'][:20])}(self):\n"
            code += f"        self._test_id = '{uc['id']}-HP-{i+1:02}'\n"
            code += f"        self._uc_id = '{uc['id']}'\n"
            code += f"        self._test_category = 'Happy Path'\n"
            code += f"        self._scenario = '{hp['scenario'].replace('\'', '')}'\n"
            code += f"        self._preconditions = '{hp['preconditions'].replace('\'', '')}'\n"
            code += f"        self._input_action = '{hp['input_action'].replace('\'', '')}'\n"
            code += f"        self._expected_result = '{hp['expected_result'].replace('\'', '')}'\n"
            code += f"        self._record_result('Not Implemented', 'Fail', 'Auto-generated stub')\n\n"
            
        for i, ap in enumerate(uc.get("alternate_paths", [])):
            code += f"    def test_ap{i+1}_{sanitize(ap['scenario'][:20])}(self):\n"
            code += f"        self._test_id = '{uc['id']}-AP-{i+1:02}'\n"
            code += f"        self._uc_id = '{uc['id']}'\n"
            code += f"        self._test_category = 'Alternate Path'\n"
            code += f"        self._scenario = '{ap['scenario'].replace('\'', '')}'\n"
            code += f"        self._preconditions = '{ap['preconditions'].replace('\'', '')}'\n"
            code += f"        self._input_action = '{ap['input_action'].replace('\'', '')}'\n"
            code += f"        self._expected_result = '{ap['expected_result'].replace('\'', '')}'\n"
            code += f"        self._record_result('Not Implemented', 'Fail', 'Auto-generated stub')\n\n"

        for i, ex in enumerate(uc.get("exception_paths", [])):
            code += f"    def test_ex{i+1}_{sanitize(ex['scenario'][:20])}(self):\n"
            code += f"        self._test_id = '{uc['id']}-EX-{i+1:02}'\n"
            code += f"        self._uc_id = '{uc['id']}'\n"
            code += f"        self._test_category = 'Exception'\n"
            code += f"        self._scenario = '{ex['scenario'].replace('\'', '')}'\n"
            code += f"        self._preconditions = '{ex['preconditions'].replace('\'', '')}'\n"
            code += f"        self._input_action = '{ex['input_action'].replace('\'', '')}'\n"
            code += f"        self._expected_result = '{ex['expected_result'].replace('\'', '')}'\n"
            code += f"        self._record_result('Not Implemented', 'Fail', 'Auto-generated stub')\n\n"
            
    with open(os.path.join(base_path, "test_use_cases.py"), "w") as f:
        f.write(code)

def generate_br():
    with open(os.path.join(base_path, "specs", "business_rules.yaml"), "r") as f:
        data = yaml.safe_load(f)
        
    code = "from .conftest import BRTestBase\n\n"
    for br in data.get("business_rules", []):
        cls_name = f"Test{sanitize(br['id'].replace('-',''))}_{sanitize(br['title'].replace(' ', ''))}"
        code += f"class {cls_name}(BRTestBase):\n"
        code += f"    \"\"\"{br['id']}: {br['title']}\"\"\"\n\n"
        
        for i, vt in enumerate(br.get("valid_tests", [])):
            code += f"    def test_valid_{i+1:02}(self):\n"
            code += f"        self._test_id = '{br['id']}-V-{i+1:02}'\n"
            code += f"        self._br_id = '{br['id']}'\n"
            code += f"        self._test_category = 'Valid'\n"
            code += f"        self._input_action = '{vt['input_action'].replace('\'', '')}'\n"
            code += f"        self._expected_result = '{vt['expected_result'].replace('\'', '')}'\n"
            code += f"        self._record_result('Not Implemented', 'Fail', 'Auto-generated stub')\n\n"
            
        for i, it in enumerate(br.get("invalid_tests", [])):
            code += f"    def test_invalid_{i+1:02}(self):\n"
            code += f"        self._test_id = '{br['id']}-I-{i+1:02}'\n"
            code += f"        self._br_id = '{br['id']}'\n"
            code += f"        self._test_category = 'Invalid'\n"
            code += f"        self._input_action = '{it['input_action'].replace('\'', '')}'\n"
            code += f"        self._expected_result = '{it['expected_result'].replace('\'', '')}'\n"
            code += f"        self._record_result('Not Implemented', 'Fail', 'Auto-generated stub')\n\n"

    with open(os.path.join(base_path, "test_business_rules.py"), "w") as f:
        f.write(code)

def generate_wf():
    with open(os.path.join(base_path, "specs", "workflows.yaml"), "r") as f:
        data = yaml.safe_load(f)
        
    code = "from .conftest import WFTestBase\n\n"
    for wf in data.get("workflows", []):
        cls_name = f"Test{sanitize(wf['id'].replace('-',''))}_{sanitize(wf['title'].replace(' ', ''))}"
        code += f"class {cls_name}(WFTestBase):\n"
        code += f"    \"\"\"{wf['id']}: {wf['title']}\"\"\"\n\n"
        
        for i, e2e in enumerate(wf.get("e2e_tests", [])):
            code += f"    def test_e2e_{i+1:02}(self):\n"
            code += f"        self._test_id = '{wf['id']}-E2E-{i+1:02}'\n"
            code += f"        self._wf_id = '{wf['id']}'\n"
            code += f"        self._test_category = 'End-to-End'\n"
            code += f"        self._scenario = '{e2e['scenario'].replace('\'', '')}'\n"
            code += f"        self._expected_final_state = '{e2e['expected_final_state'].replace('\'', '')}'\n"
            code += f"        self._add_step(1, 'Auto step', 'Any', 'None', False)\n"
            code += f"        self._record_result('Not Implemented', 'Fail', 'Auto-generated stub')\n\n"
            
        for i, neg in enumerate(wf.get("negative_tests", [])):
            code += f"    def test_neg_{i+1:02}(self):\n"
            code += f"        self._test_id = '{wf['id']}-NEG-{i+1:02}'\n"
            code += f"        self._wf_id = '{wf['id']}'\n"
            code += f"        self._test_category = 'Negative'\n"
            code += f"        self._scenario = '{neg['scenario'].replace('\'', '')}'\n"
            code += f"        self._expected_final_state = '{neg['expected_final_state'].replace('\'', '')}'\n"
            code += f"        self._add_step(1, 'Auto step', 'Any', 'None', False)\n"
            code += f"        self._record_result('Not Implemented', 'Fail', 'Auto-generated stub')\n\n"

    with open(os.path.join(base_path, "test_workflows.py"), "w") as f:
        f.write(code)

generate_uc()
generate_br()
generate_wf()
print("Generated all tests!")
