#!/bin/bash
sleep 2

FIREFOX=$(which firefox)

$FIREFOX --kiosk http://localhost
