import re, sys, data, requests, json, time, os
from web3 import Web3, Account

with open("config.json", "r") as file:
    config = json.load(file)

privateKey = config["privateKey"]
publicKey = Account.from_key(privateKey).address
account = Account.from_key(privateKey)
config["publicKey"] = publicKey
with open('config.json', 'w') as file:
    json.dump(config, file, indent=4)

chainId = config["chainId"]

RPCProvider = config["RPCProvider"]
w3 = Web3(Web3.HTTPProvider(RPCProvider))

def sendEther():
    global chainId
    global w3
    while True:
        print("Enter recepient's address")
        recAddress = input(">> ")
        if re.match(r"^0x[a-fA-F0-9]{40}$", recAddress):
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

def checkBalance():
    global chainId
    balance = w3.eth.get_balance(publicKey)
    balance = w3.from_wei(balance, 'ether')
    print(f"Wallet contains {balance} ETH")
    print(f"(Address: {publicKey})")

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

def printAddress():
    print(publicKey)

def exitProgram():
    sys.exit()

def Continue(message):
    while True:
        response = input(message + "\n[Y]/[n]\n>> ")
        if response in ["Y", "", "y"]:
            return True
        elif response in ["N", "n"]:
            return False
        else:
            print("\nIncorrect Input\n") 

def printChainId():
    global chainId
    print(f"The current chain ID is {chainId}")

def selectChainId():
    global chainId
    print(f"Current chain ID is {chainId}")
    print("Enter the new chain ID")
    chainId = int(input(">> "))
    global config
    config["chainId"] = chainId
    with open('config.json', 'w') as file:
        json.dump(config, file, indent=4)

def clearScreen():
    os.system('cls' if os.name == 'nt' else 'clear')

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
        "0": exitProgram
    }    

    while True:
        time.sleep(1)
        print("\nOptions:")
        print("[1] Send Ether")
        print("[2] Check Balance")
        print("[3] Print Address")
        print("[4] Check RPC Provider")
        print("[5] Change RPC Provider")
        print("[6] Print current chain ID")
        print("[7] Select new chain ID")
        print("[8] Clear screen")
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
    print(visual)
    print("Welcome to ZEPHYR Wallet")
    pickOptions()

welcome()
