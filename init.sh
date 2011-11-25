#!/bin/bash

if test -x `which pip` && test -x `which virtualenv`; then
    echo "Creating the virtual environment, please wait..."
    virtualenv --no-site-packages ./env
    source ./env/bin/activate
    echo "Creating cache directories"
    mkdir -p ./caches/{apt,pip,other}
    echo "Installing packages into the environment, please wait..."
    pip install --download-cache=./caches/pip -E ${VIRTUAL_ENV} -r reqs/devel.txt
else
    echo "Install 'pip' and 'virtualenv' manually."
    if test -x `which apt-get`; then
        echo -e "Use:\n\tapt-get install python-setuptools python-virtualenv"
    else
        echo -e "Use:\n\teasy_install setuptools\n\teasy_install virtualenv"
    fi
    exit 1
fi

echo "Put your code into 'src' directory."
mkdir ./src

exit 0
