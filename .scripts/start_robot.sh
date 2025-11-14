#!/bin/bash
echo 'Powering on robot! (Is it about to drive off a table?)'

echo "Running ansible command now!"
# bash -c './ansible/ansible_comhand.py START self WITH smartbot3_ws >> hardware_software:dev'

sleep 2
echo '[WOOP WOOP] Robot now active!'
exit 0