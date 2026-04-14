#!/usr/bin/sh

ENGINE_PATH=./engine

# We will also want to start the oracle database daemon presumably? Does it have one of those?
docker compose up -d

# Server In, Engine Out and vice versa.
rm -rf SIEO_PIPE SOEI_PIPE

mkfifo SIEO_PIPE SOEI_PIPE

python main.py < SIEO_PIPE > SOEI_PIPE &
$ENGINE_PATH > SIEO_PIPE < SOEI_PIPE

rm -rf SIEO_PIPE SOEI_PIPE
