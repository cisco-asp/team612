from connect_pyats import collect_raw_outputs
import os

testbed = "testbed.yml"
router = "xr-8"
commands = ["show run"]

results = collect_raw_outputs(testbed, router, commands)
file_path = os.path.join(f"router_configs/{router}_running_config.txt")
for cmd, output in results.items():

    with open(file_path, "w") as f:
        f.write(output)