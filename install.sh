#!/bin/bash

function ubuntu_precise {
    sudo aptitude install python-virtualenv make
    make tests
}

printf "Target operating system [precise]: "
while read options; do
  case "$options" in
    "")         ubuntu_precise
                ;;
    precise)    ubuntu_precise
                ;;
    *) printf "Incorrect value option!\nPlease enter the correct value: " ;;
  esac
done
