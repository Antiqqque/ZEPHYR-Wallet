import base64
import hashlib
import json
import os
import re
import socket
import sys
import time

import requests
from cryptography.fernet import Fernet
from web3 import Account, Web3

# Loads values from config.json

with open("config.json", "r") as file:
    config = json.load(file)
if config["encryptedPrivateKey"] == "":
    encryptedPrivateKey = ""
else:
    encryptedPrivateKey = config["encryptedPrivateKey"].encode()
chainId = config["chainId"]
RPCProvider = config["RPCProvider"]
publicKey = config["publicKey"]
privateKey = ""

# Creates a web3 object for interactions with the RPC

w3 = Web3(Web3.HTTPProvider(RPCProvider))

# Checks the validity of a private key


def checkPrivateKeyValidity(privateKey):
    if not privateKey.startswith(b"0x"):
        return False
    privateKey = privateKey[2:]  # Remove the "0x" prefix
    if len(privateKey) != 64:
        return False
    try:
        int(privateKey, 16)
    except TypeError:
        return False
    return True


# Generates a fresh private-public key pair for the user


def generatePrivateKey():
    privateKey = Account.create()._private_key.hex()
    publicKey = Account.from_key(privateKey).address
    print("\nNew Private-Public key pair generated\n")
    print(f"Private key: {privateKey}")
    print(f"Public key: {publicKey}")
    return privateKey, publicKey


# Allows the user to import their own private key, and generates the corresponding public key


def importPrivateKey():
    print("Input private key")
    privateKey = input(">> ")
    privateKey = privateKey.encode()
    if checkPrivateKeyValidity(privateKey):
        print("Private key is correct...")
        privateKey = privateKey.decode("utf-8")
        publicKey = Account.from_key(privateKey).address
        print(f"Matching address: {publicKey}")
        return privateKey, publicKey
    else:
        print("Private key is invalid, try again")
        importrivateKey()


# Initializes the password-based encryption, and stores the private key in an encrypted format


def initializePrivateKeyPasswordEncryption(privateKey, publicKey):
    print("\nCreate a password to encrypt the private key")
    passwd = input(">> ")
    print("\nRepeat password")
    passwd2 = input(">> ")
    if passwd == passwd2:
        print("\nPasswords match")
        print("\nEncrypting keys...")
        key = createKeyFromPassword(passwd)
        encryptedPrivateKey = encryptPrivateKey(privateKey, key)
        config[
            "encryptedPrivateKey"
        ] = (
            encryptedPrivateKey.decode()
        )  # Write the encrypted private key and public key to config.json
        config["publicKey"] = publicKey
        with open("config.json", "w") as file:  #
            json.dump(config, file, indent=4)
        print("\nEncryption succsesful\n")
    else:
        print("Passwords don't match")
        initializePasswordEncryption()


# Creates an encryption key from a password


def createKeyFromPassword(password):
    key = hashlib.sha256(password.encode()).digest()
    key = base64.urlsafe_b64encode(key)
    return key


# Encrypts the private key using a previously generated key


def encryptPrivateKey(privateKey, key):
    fernet = Fernet(key)
    encryptedPrivateKey = fernet.encrypt(privateKey.encode())
    return encryptedPrivateKey


# Decrypts the private key using a previously generated key


def decryptPrivateKey(encryptedPrivateKey, key):
    fernet = Fernet(key)
    privateKey = fernet.decrypt(encryptedPrivateKey.decode())
    return privateKey


# Validates the password by checking whether the decrypted key is a valid private key


def validatePassword(password, encryptedPrivateKey):
    try:
        key = createKeyFromPassword(password)
        privateKey = decryptPrivateKey(encryptedPrivateKey, key)
        return checkPrivateKeyValidity(privateKey)
    except ValueError:
        return False


# Starts the sign-up proccess


def signUp():
    print("No private key found")
    print("[1] Generate new private key")
    print("[2] Import existing private key")
    q = input(
        ">> "
    )  # Gives the choice between generating a new key or importing an existing one
    if q == "1":
        privateKey, publicKey = generatePrivateKey()
    elif q == "2":
        privateKey, publicKey = importPrivateKey()
    else:
        print("Incorrect option")
    initializePrivateKeyPasswordEncryption(
        privateKey, publicKey
    )  # Prompts the user to create a password,
    # then encrypts the private key, and stores it


# Logs the user in


def login():
    global privateKey
    global encryptedPrivateKey
    print("Enter your password:")
    password = input(">> ")
    if validatePassword(password, encryptedPrivateKey):
        print("\n<[Successfully logged in]>")
        key = createKeyFromPassword(password)
        privateKey = decryptPrivateKey(encryptedPrivateKey, key).decode(
            "utf-8"
        )  # decodes the private key and allows it to be used by the program
        pickOptions()
        return False
    else:
        print("\nIncorrect password, try again\n")
        login()


# Dialogue box - [Y]/[n]


def Continue(message):
    response = input(message + "\n[Y]/[n]\n>> ")
    if response in ["Y", "", "y"]:
        return True
    elif response in ["N", "n"]:
        return False
    else:
        print("\nIncorrect Input\n")
        Continue()


# Sends Ether to a desired address


def sendEther():
    global chainId
    global w3
    while True:
        print("Enter recepient's address")
        recAddress = input(">> ")
        if re.match(
            r"^0x[a-fA-F0-9]{40}$", recAddress
        ):  # Uses an algorithm to check whether the input is a valid Ethereum address
            print(f"Enter amount of ETH to send to {recAddress}")
            sendAmount = input(">> ")
            transaction = {
                "to": recAddress,
                "value": w3.to_wei(sendAmount, "ether"),
                "gas": 21000,
                "gasPrice": w3.to_wei("50", "gwei"),
                "nonce": w3.eth.get_transaction_count(account.address),
                "chainId": chainId,
            }
            # Converts the costs of the transaction to ether, rounds it to the 6th decimal
            gas_price = round(float(w3.from_wei(w3.eth.gas_price * 21000, "ether")), 6)
            sendAmount = round(float(sendAmount), 6)
            totalCost = round(gas_price + sendAmount, 6)
            print("___________________________")
            print(f"\nGas price is {gas_price} ETH")
            print(f"Full transaction cost is {totalCost} ETH")
            print(f"Send {sendAmount} ETH to {recAddress}?")
            q = Continue(
                "Proceed with transaction?"
            )  # Asks one final time whether to proceed with the transaction
            if q:
                print("\nProceeding...\n")
                signed_tx = account.sign_transaction(transaction)
                tx_hash = w3.eth.send_raw_transaction(
                    signed_tx.rawTransaction
                )  # Sends the transaction to the RPC
                print("Transaction sent. Hash:", tx_hash.hex())
                return False
            else:
                print("Aborting...")
                return True
        else:
            q = Continue("Incorrect address, try again?")
            if not q:
                return False


# Checks the balance of the user using the RPC


def checkBalance():
    balance = w3.eth.get_balance(publicKey)
    balance = w3.from_wei(balance, "ether")
    print(f"Wallet contains {balance} ETH")
    print(f"(Address: {publicKey})")


# Checks whether the RPC is online by making a request


def checkRPC():
    global RPCProvider
    try:
        response = requests.get(RPCProvider)
        if response.status_code == 200:
            print(f"RPC provider {RPCProvider} is online")
        else:
            print(f"RPC provider {RPCProvider} is offline")
    except socket.error as e:
        print("A network error occurred:", str(e))


# Changes the RPC to a new URL, no validity check, however the user can use the
# checkRPC() and checkBalance() functions to see if it's operational


def changeRPC():
    global RPCProvider
    global w3
    print(f"\nOld RPC is {RPCProvider}\nInput new RPC:")
    newRPC = input(">> ")
    print(f"\nNew RPC is {newRPC}")
    RPCProvider = newRPC
    global config
    config["RPCProvider"] = newRPC
    with open("config.json", "w") as file:
        json.dump(config, file, indent=4)
    w3 = Web3(Web3.HTTPProvider(RPCProvider))


# prints the address of the user


def printAddress():
    print(publicKey)


# Exits the program


def exitProgram():
    sys.exit()


# Print's the current EVM chain ID


def printChainId():
    global chainId
    print(f"The current chain ID is {chainId}")


# Changes the EVM Chain ID


def selectChainId():
    global chainId
    print(f"Current chain ID is {chainId}")
    print("Enter the new chain ID")
    chainId = int(input(">> "))
    config["chainId"] = chainId
    with open("config.json", "w") as file:
        json.dump(config, file, indent=4)


# Clears the screen for the user


def clearScreen():
    os.system("cls" if os.name == "nt" else "clear")


# Wallet choice menu


def exportPrivateKey():
    print(f"Your private key is: {privateKey}\n")


# Allows the user to pick options once they have logged in 


def pickOptions():
    options = {
        "1": sendEther,
        "2": checkBalance,
        "3": printAddress,
        "4": checkRPC,
        "5": changeRPC,
        "6": printChainId,
        "7": selectChainId,
        "8": clearScreen,
        "9": exportPrivateKey,
        "0": exitProgram,
    }

    while True:
        time.sleep(1)
        print("__________________________")
        print("Options:")
        print("[1] Send Ether")
        print("[2] Check Balance")
        print("[3] Print Address")
        print("[4] Check RPC Provider")
        print("[5] Change RPC Provider")
        print("[6] Print Current Chain ID")
        print("[7] Select New Chain ID")
        print("[8] Clear Screen")
        print("[9] Export Private Key")
        print("[0] Exit")
        print("__________________________")

        x = input(">> ")
        print()
        options.get(x, lambda: print("Invalid option. Please select a valid option."))()


visual = """
____________________________________

                         <-     <- 
              __________    <-
             |~~_~__ _  |        <-
             ) (ZEPHYR) (    <- 
             |-_________| <-
                            <-
                               <-
____________________________________
"""


# main function loop


def welcome():
    print("\nWelcome to ZEPHYR Wallet")
    print(visual)
    if encryptedPrivateKey == "":
        signUp()
    else:
        login()


welcome()
