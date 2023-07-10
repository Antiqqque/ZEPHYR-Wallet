# ZEPHYR-Wallet
A simple wallet for Ethereum and EVM-compatible chains that grants one the ability to send simple transactions
and view your balance.

Doesn't store or send any personal data like IP address to anyone, except the chosen RPC provider, but even that can be mitigated by running the wallet through a proxy service or by using a VPN

## Installation

1. Make sure you have Python installed on your system. You can download the latest version of Python from the official website: [python.org](https://www.python.org/downloads/) or use a package manager to install it.

2. Pip is the package installer for Python. If you have installed Python using the official installer, pip should already be installed. You can verify its installation by running the following command in your terminal:

pip --version

If pip is not installed, you can install it by following the instructions provided in the official pip documentation: pip.pypa.io/en/stable/installing/

3. Install project dependencies

This project has dependencies listed in the requirements.txt file. To install them, navigate to the project directory in your terminal and run the following command:

pip install -r requirements.txt

##  Usage

Simply run zephyr.py by typing python zephyr.py

## Security

The private key is stored in an encrypted fashion in the config.json file. In case of file corruption, back up the file. To decrypt the private key you will need the password you entered at sign-up
