#!/bin/bash

KLIPPER_PATH="${HOME}/klipper"
TMC4671_PATH="${HOME}/tmc-4671"

if [[ -e ${KLIPPER_PATH}/klippy/plugins/ ]]; then
    KLIPPER_PLUGINS_PATH="${KLIPPER_PATH}/klippy/plugins/"
else
    KLIPPER_PLUGINS_PATH="${KLIPPER_PATH}/klippy/extras/"
fi

set -eu
export LC_ALL=C

function preflight_checks {
    if [ "$EUID" -eq 0 ]; then
        echo "[PRE-CHECK] This script must not be run as root!"
        exit -1
    fi

    if [ "$(sudo systemctl list-units --full -all -t service --no-legend | grep -F 'klipper.service')" ]; then
        printf "[PRE-CHECK] Klipper service found! Continuing...\n\n"
    else
        echo "[ERROR] Klipper service not found, please install Klipper first!"
        exit -1
    fi
}

function check_download {
    local tmc4671dirname tmc4671basename
    tmc4671dirname="$(dirname ${TMC4671_PATH})"
    tmc4671basename="$(basename ${TMC4671_PATH})"

    if [ ! -d "${TMC4671_PATH}" ]; then
        echo "[DOWNLOAD] Downloading TMC4671 repository..."
        if git -C $tmc4671dirname clone https://github.com/andrewmcgr/tmc-4671.git $tmc4671basename; then
            chmod +x ${TMC4671_PATH}/install.sh
            printf "[DOWNLOAD] Download complete!\n\n"
        else
            echo "[ERROR] Download of TMC4671 git repository failed!"
            exit -1
        fi
    else
        printf "[DOWNLOAD] TMC4671 repository already found locally. Continuing...\n\n"
    fi
}

function link_extension {
    echo "[INSTALL] Linking extension to Klipper..."

    ln -srfn "${TMC4671_PATH}/tmc4671.py" "${KLIPPER_PLUGINS_PATH}/tmc4671.py"
}

function restart_klipper {
    echo "[POST-INSTALL] Restarting Klipper..."
    sudo systemctl restart klipper
}

printf "\n======================================\n"
echo "- TMC4671 install script -"
printf "======================================\n\n"

# Run steps
preflight_checks
check_download
link_extension
restart_klipper
