#!/usr/bin/env bash

~$ python -m screaper.core.main | tee 1.log & python -m screaper.core.main | tee 2.log &  python -m screaper.core.main | tee 3.log

trap 'kill %1' SIGINT
python -m screaper.core.main | tee 1.log | sed -e 's/^/[Command1] /' & python -m screaper.core.main | tee 2.log | sed -e 's/^/[Command2] /'



python -m screaper.core.main | tee 1.log | sed -e 's/^/[Command1] /' & python -m screaper.core.main | tee 2.log | sed -e 's/^/[Command2] /' & python -m screaper.core.main | tee 3.log | sed -e 's/^/[Command3] /' & python -m screaper.core.main | tee 4.log | sed -e 's/^/[Command4] /'
