# team612
SR-DPM Splunk Use-case

## Rebuild Webhook Flask API app on host ###

docker-compose down -v
docker system prune -f
docker-compose build --no-cache
docker-compose up -d

## Test Webhook API ##

curl -X POST http://localhost:5000/splunk-webhook/dpm \
  -H "Content-Type: application/json" \
  -d @alert_dpm.json

curl -X POST http://localhost:5100/splunk-webhook/l2vpn \
  -H "Content-Type: application/json" \
  -d @alert_l2vpn.json


## aliases xr-5, xr-8 ##

alias exec dpm1 show run mpls oam
alias exec dpm2 show mpls oam dpm prefix
alias exec dpm3 show route 10.0.0.1/32 detail
alias exec dpm4 show mpls forwarding labels 16001
alias exec dpm5 show mpls oam dpm prefix faults 
alias exec dpm7 run rib_lib_test -f corrupt_label_xr5.txt

## process to corrupt a label ##

1.  show current config
  dpm1
2.  show normal working state
  dpm4
  dpm2 - note there should be 0 errors, but a timestamp for last known failure
  dpm5 - this will show nothing unless there is a current error
3. corrupt the label
  open new session on xr-2
  dpm7
4. go back to first session - show corrupt state 
  dpm4
5. Wait for error to be picked up by dpm process
  dpm2 - once you see an error in the 16008 label's error column
  dpm5 - see the fault

