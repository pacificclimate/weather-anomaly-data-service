#!/bin/bash
adduser --disabled-password --gecos '' user
adduser user sudo
echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers