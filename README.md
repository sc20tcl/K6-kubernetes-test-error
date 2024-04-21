teastore-clusterip.yaml -
  The deployment configuration of the TeaStore web ui.

testOrchestrator.py -
  The python script that instantiates a series of k6 load tests at different number of virtual users for a predefined period of time.

K6Job.js -
  The K6 script that actually runs the individual test. For each virtual user request the script selects a http at random from a predefined list.

  
