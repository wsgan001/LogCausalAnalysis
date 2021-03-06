# LogCausalAnalysis

## Overview

This project provides a series of functions to analyze 
system log data in terms of event causality.

* Classify log data with its output format
* Generate DAG with PC algorithm (using pcalg/gsq package)
* Process log incrementally and notify troubles <- work in progress

## Package requirements

* pcalg https://github.com/keiichishima/pcalg
* gsq https://github.com/keiichishima/gsq

## Tutorial

You can generate pseudo log dataset for testing functions.

$ python testlog.py > test.temp

First, you need to generate a configuration file for whole system.
Copy sample file, and edit it if necessary.

$ cp config.conf.sample config.conf

Then classify dataset and register them with database.
Classification works with log template generation inside this command.

$ python log_db.py -c config.conf make

You can see log templates found in log messages with following command.

$ python log_db.py -c config.conf show-lt

Then analyze causal relations generating DAG.
(This step requires much time. If your machine have enough performance,
we recommend you to use -p options for multithreading.)

$ python pc_log.py

You can check result DAG with following command.

$ python pcresult.py -g graph.pdf show pc_output/all_21120901

