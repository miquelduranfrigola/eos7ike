# imports
import os
import csv
import sys
import subprocess
import tempfile

# get path of current python executable
python_executable = sys.executable

# parse arguments
input_file = sys.argv[1]
output_file = sys.argv[2]

# current file directory
root = os.path.dirname(os.path.abspath(__file__))

# read SMILES from .csv file, assuming one column with header
with open(input_file, "r") as f:
    reader = csv.reader(f)
    next(reader)  # skip header
    smiles_list = [r[0] for r in reader]

tmp_folder = tempfile.mkdtemp()
input_tmp = os.path.join(tmp_folder, "input.smi")
with open(input_tmp, "w") as f:
    for i, smi in enumerate(smiles_list):
        f.write(f"{smi} mol_{i}\n")

bash_file = os.path.join(tmp_folder, "run_model.sh")
bash_content = f"""
{python_executable} -c "import site; print(site.getsitepackages()[0])";

SITEPKG=$({python_executable} -c "import site; print(site.getsitepackages()[0])")
cat > "$SITEPKG/sitecustomize.py" <<'PY'
try:
    from openbabel import openbabel as ob
    # Provide legacy symbol expected by old code:
    if not hasattr(ob, "OBForceField_FindType") and hasattr(ob, "OBForceField"):
        if hasattr(ob.OBForceField, "FindType"):
            ob.OBForceField_FindType = ob.OBForceField.FindType
        elif hasattr(ob.OBForceField, "FindForceField"):
            ob.OBForceField_FindType = ob.OBForceField.FindForceField
except Exception:
    # Don't break interpreter startup if openbabel isn't installed in some envs
    pass
PY;

{python_executable} {root}/entry-cli/calc_props.py -b {input_tmp} -o {output_tmp}

"""


#check input and output have the same lenght
input_len = len(smiles_list)
output_len = len(outputs)
assert input_len == output_len

# write output in a .csv file
with open(output_file, "w") as f:
    writer = csv.writer(f)
    writer.writerow(["value"])  # header
    for o in outputs:
        writer.writerow([o])
