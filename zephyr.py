import re, sys, requests, json, time, os
from web3 import Web3, Account
from cryptography.fernet import Fernet
import hashlib
import base64

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
    except ValueError:
        return False
    return True


# Generates a new private-public key pair, encrypts the private key,
# and stores them at sign-uper

def generatePrivateKey(): 
    global encryptedPrivateKey
    global config
    privateKey = Account.create()._private_key.hex()
    publicKey = Account.from_key(privateKey).address
    print("New Private-Public key pair generated")
    print(f"Private key: {privateKey}")
    print(f"Public key: {publicKey}")
    while True:
        print("Create a password to encrypt the private key")
        passwd = input(">> ")
        print("Repeat password")
        passwd2 = input(">> ")
        if passwd == passwd2:
            print("\nPasswords match")
            print("\nEncrypting keys...")
            key = createKeyFromPassword(passwd)
            encryptedPrivateKey = encryptPrivateKey(privateKey, key)

            config["encryptedPrivateKey"] = encryptedPrivateKey.decode() # Write the encrypted private key and public key to config.json
            config["publicKey"] = publicKey
            with open('config.json', 'w') as file: #
                json.dump(config, file, indent=4)

            print("Encryption succsesful\n")
            return False
        else:
            print("Passwords don't match")

# Encrypts and stores the private key of the user at sign-up

def storePrivateKey():
    global config
    print("Input private key")
    privateKey = input(">> ")
    privateKey = privateKey.encode()
    if checkPrivateKeyValidity(privateKey):
        print("Private key is correct...")
        privateKey = privateKey.decode("utf-8") 
        publicKey = Account.from_key(privateKey).address
        print(f"Matching address: {publicKey}")
        while True:
            print("Create a password to encrypt the private key")
            passwd = input(">> ")
            print("Repeat password")
            passwd2 = input(">> ")
            if passwd == passwd2:
                print("\nPasswords match")
                print("\nEncrypting keys...")
                key = createKeyFromPassword(passwd)
                encryptedPrivateKey = encryptPrivateKey(privateKey, key) 

                config["encryptedPrivateKey"] = encryptedPrivateKey.decode() # Write the encrypted private key and public key to config.json
                config["publicKey"] = publicKey
                with open('config.json', 'w') as file: #
                    json.dump(config, file, indent=4)

                print("Encryption succsesful\n")
                return False
            else:
                print("Passwords don't match")

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

def validatePassword(password):
    global encryptedPrivateKey
    try:
        key = createKeyFromPassword(password)
        privateKey = decryptPrivateKey(encryptedPrivateKey, key)
        return checkPrivateKeyValidity(privateKey)
    except:
        ValueError

# Starts the sign-up proccess

def signUp():
    print("No private key found")
    print("[1] Generate new private key")
    print("[2] Import existing private key")
    q = input(">> ")
    if q == "1":
        generatePrivateKey()
    elif q == "2":
        storePrivateKey()
    else:
        print("Incorrect option")

# Logs the user in

def login():
    global privateKey
    global encryptedPrivateKey
    while True:
        print("Enter your password:")
        password = input(">> ")
        if validatePassword(password):
            print("\n<[Successfully logged in]>")
            key = createKeyFromPassword(password)
            privateKey = decryptPrivateKey(encryptedPrivateKey, key).decode('utf-8') # decodes the private key and allows it to be used by the program
            pickOptions()
            return False
        else:
            print("\nIncorrect password, try again\n")

# Sends Ethereum to a desired address

def sendEther():
    global chainId
    global w3
    while True:
        print("Enter recepient's address")
        recAddress = input(">> ")
        if re.match(r"^0x[a-fA-F0-9]{40}$", recAddress): # Uses an algorithm to check whether the input is a valid Ethereum address
            print(f"Enter amount of ETH to send to {recAddress}")
            sendAmount = input(">> ")
            transaction = {
                'to': recAddress,
                'value': w3.to_wei(sendAmount, 'ether'),
                'gas': 21000,
                'gasPrice': w3.to_wei('50', 'gwei'),
                'nonce': w3.eth.get_transaction_count(account.address),
                'chainId': chainId
            }
            gas_price = round(float(w3.from_wei(w3.eth.gas_price * 21000, "ether")), 6)
            sendAmount = round(float(sendAmount), 6)
            totalCost = round(gas_price + sendAmount, 6)
            print("___________________________")
            print(f"\nGas price is {gas_price} ETH")
            print(f"Full transaction cost is {totalCost} ETH")
            print(f"Send {sendAmount} ETH to {recAddress}?")
            q = Continue("Proceed with transaction?")
            if q:
                print("\nProceeding...\n")
                signed_tx = account.sign_transaction(transaction)
                tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                print("Transaction sent. Hash:", tx_hash.hex())
                return False
            else:
                print("Aborting...")
                return True
        else:
            q = Continue("Incorrect address, try again?")
            if not q:
                return False

# Checks the balance of the user through the RPC

def checkBalance():
    global chainId
    balance = w3.eth.get_balance(publicKey)
    balance = w3.from_wei(balance, 'ether')
    print(f"Wallet contains {balance} ETH")
    print(f"(Address: {publicKey})")

# Checks whether the RPC URL is online by making a request

def checkRPC():
    global RPCProvider
    try:
        response = requests.get(RPCProvider)
        if response.status_code == 200:
            print(f"RPC provider {RPCProvider} is online")
        else:
            print(f"RPC provider {RPCProvider} is offline")
    except requests.exceptions.RequestException:
        print("Error - unknown exception")

# Changes the RPC to a new URL, no validity check, however the user can use the
# checkRPC() function to see if it's operational

def changeRPC():
    global RPCProvider
    global w3
    print(f"\nOld RPC is {RPCProvider}\nInput new RPC:")
    newRPC = input(">> ")
    print(f"\nNew RPC is {newRPC}")
    RPCProvider = newRPC
    global config
    config["RPCProvider"] = newRPC
    with open('config.json', 'w') as file:
        json.dump(config, file, indent=4)
    w3 = Web3(Web3.HTTPProvider(RPCProvider))

# prints the address of the user

def printAddress():
    print(publicKey)

def exitProgram():
    sys.exit()

# Dialogue box - [Y]/[n]

def Continue(message):
    while True:
        response = input(message + "\n[Y]/[n]\n>> ")
        if response in ["Y", "", "y"]:
            return True
        elif response in ["N", "n"]:
            return False
        else:
            print("\nIncorrect Input\n") 

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
    global config
    config["chainId"] = chainId
    with open('config.json', 'w') as file:
        json.dump(config, file, indent=4)

# Clears the screen for the user

def clearScreen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Wallet choice menu

def exportPrivateKey():
    print(f"Your private key is: {privateKey}\n")

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
        "0": exitProgram
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

def welcome():
    print("\nWelcome to ZEPHYR Wallet")
    print(visual)
    if encryptedPrivateKey == "":
        signUp()
    else:
        login()

welcome()
