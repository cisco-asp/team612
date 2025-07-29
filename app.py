from flask import Flask, request, jsonify
from publish_message import send_webex_message, send_webex_file_message
from connect_netmiko import run_command
from jinja2 import Template
from connect_pyats import collect_raw_outputs, collect_parsed_outputs
from render_config import render_yaml_template
import logging
import json
import os

app = Flask(__name__)

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Configure logging to file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler("logs/splunk_alerts.log"),
        logging.StreamHandler()  # Optional: still print to console
    ]
)

def log_alert(alert_type, data):
    logging.info(f"[{alert_type}] Received Splunk alert:")
    logging.info(json.dumps(data, indent=2))

@app.route('/splunk-webhook/l2vpn', methods=['POST'])
def receive_l2vpn_alert():
    # TODO fix splunk alert to give router and circuit in POST
    router = "xr-8"
    circuit = "TMO-21"
    # Pull in commands and message
    context = {"xc_name": circuit}
    data = render_yaml_template("config.yml.j2", context)
    commands = [cmd["command"] for cmd in data["l2vpn"]["commands"]]
    try:
        alert_data = request.get_json(force=True)
        log_alert("L2VPN", alert_data)


        # xconnect_detail = f'show l2vpn xconnect group MBH xc-name {circuit} detail'
        # commands = [xconnect_detail,
        #     'show segment-routing traffic-eng policy',
        #     'show performance-measurement sr-policy'
        #     ]

        run_commands = '\n'.join(commands)
        message = f"""
# High Value Customer has a Service down!\n\n
An Error was detected on router **{router.upper()}** with Circuit ID - **{circuit}** by Splunk
---
### SLA's are being violated
---
## Diagnostics incoming! 
_Please Standby_ I am gathering these command outputs
```
{run_commands}
```
"""
        response = send_webex_message(
            bot_token,
            room_id,
            markdown_message=message,
        )

        print(json.dumps(response["created"], indent=2))


        outputs = []
        for command in commands:
            output = run_command(
                host='198.18.133.8',
                username='cisco',
                password='cisco123',
                command=command
            )
            outputs.append(output)


        formatted_outputs = '\n'.join(f"------{x}------\n{y}\n" for x,y in zip(commands, outputs))
        # print(formatted_outputs)
        f_name = f"L2VPN_{router.upper()}_{circuit}.txt"
        with open(f_name, "w") as f:
            f.write(formatted_outputs)

        message = f"Diagnostic of **{router.upper()}** for ***{circuit}*** Circuit"

        response = send_webex_file_message(
            bot_token,
            room_id,
            message_text=message,
            file_path = f_name
        )

        print(response.text)
    
        return jsonify({"status": "l2vpn alert received"}), 200
    except Exception as e:
        logging.error(f"L2VPN webhook error: {str(e)}")
        return jsonify({"error": str(e)}), 400

@app.route('/splunk-webhook/dpm', methods=['POST'])
def receive_dpm_alert():
    # Pull in commands and message
    context = {"xc_name": "TMO-21"}
    data = render_yaml_template("config.yml.j2", context)
    commands = [cmd["command"] for cmd in data["dpm"]["commands"]]

    # Gather useful information from Splunk POST action
    splunk_data = request.get_json()
    router = splunk_data.get("result", {}).get("host")

    try:
        alert_data = request.get_json(force=True)
        log_alert("DPM", alert_data)

        run_commands = '\n'.join(commands)
        message = f"""
# SR-DPM Alert!
An Error was detected on router **{router.upper()}** by Splunk indicating an SR-DPM failure
## Diagnostics incoming! 
_Please Standby_ I am gathering these command outputs
```
{run_commands}
```
"""
        response = send_webex_message(
            bot_token,
            room_id,
            markdown_message=message,
        )

        print(json.dumps(response["created"], indent=2))

        outputs = []
        # TODO fix pyats integration
        # for cmd in data["dpm"]["commands"]:
        #     if cmd["type"] == "raw":
        #         print(cmd["command"], cmd["type"])
        #         output = collect_raw_outputs(testbed, router, cmd["command"])
        #     if cmd["type"] == "parse":
        #         output = collect_parsed_outputs(testbed, router, cmd["command"])
        for command in commands:
            output = run_command(
                host= router,
                username='cisco',
                password='cisco123',
                command=command
            )
            outputs.append(output)


        formatted_outputs = '\n'.join(f"------{x}------\n{y}\n" for x,y in zip(commands, outputs))
        print(formatted_outputs)
        message = f"""
Diagnostic of **{router.upper()}** router outputs
```
{formatted_outputs}
```
"""
        response = send_webex_message(
            bot_token,
            room_id,
            markdown_message=message,
        )

        print(json.dumps(response["created"], indent=2))

        return jsonify({"status": "dpm alert received"}), 200
    except Exception as e:
        logging.error(f"DPM webhook error: {str(e)}")
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    testbed = "testbed.yml"
    bot_token = os.getenv("BOT_TOKEN")
    room_id = os.getenv("ROOM_ID")
    app.run(host='0.0.0.0', port=5100)