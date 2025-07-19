from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

# Node access params
RPC_URL = "http://alice:password@127.0.0.1:18443"

def wallet_exist(client, wallet_name):
    wallets_data = client.listwalletdir()
    # print(wallets_data["wallets"])
    wallet_names = [wallet["name"] for wallet in wallets_data["wallets"]]
    return wallet_name in wallet_names

def wallet_loaded(client, wallet_name):
    wallet_list = client.listwallets()
    return wallet_name in wallet_list

def create_wallet(client, wallet_name):
    if wallet_loaded(client, wallet_name):
        return wallet_name
    
    if wallet_exist(client, wallet_name):
        return client.loadwallet(wallet_name)["name"]
    
    return client.createwallet(wallet_name)["name"]

def check_mempool(client, tx_id):
    
    try:
        mempool_txid = client.getrawmempool()

        if tx_id in mempool_txid:
            mempool_entry = client.getmempoolentry(tx_id)
            return mempool_entry
        else:
            raise ValueError(f"Transaction with id of {tx_id} not found in mempools")
    except JSONRPCException as e:
        raise ValueError(f"this error happen{e}")
    


def get_tx(client, tx_id):
    try:
        # Get transaction with verbose details and include watch-only
        tx_details = client.gettransaction(tx_id, None, True)
        return tx_details
    except Exception as e:
        raise ValueError(f"Can't get transaction for {tx_id} Error: {e}")
    
def decode_raw_tx(client, hex):
    try:
        raw_tx = client.decoderawtransaction(hex)
        return raw_tx
    except Exception as e:
        raise ValueError(f"{e}")

def main():
    try:
        # General client for non-wallet-specific commands
        client = AuthServiceProxy(RPC_URL)

        # Get blockchain info
        blockchain_info = client.getblockchaininfo()
        # print("Blockchain Info:", blockchain_info)

        # Create/Load the wallets, named 'Miner' and 'Trader'. Have logic to optionally create/load them if they do not exist or are not loaded already.

        miner_wallet = create_wallet(client, "Miner")
        trader_wallet = create_wallet(client, "Trader")
        miner_client = AuthServiceProxy(f"{RPC_URL}/wallet/{miner_wallet}")
        # trader_client = AuthServiceProxy(f"{RPC_URL}/wallet/{trader_wallet}")

        # Generate spendable balances in the Miner wallet. Determine how many blocks need to be mined.
        miner_address = miner_client.getnewaddress()

        if client.getblockcount() < 101:
            client.generatetoaddress(101, miner_address)

        # Load the Trader wallet and generate a new address.
        load_trader_client = AuthServiceProxy(f"{RPC_URL}/wallet/{trader_wallet}")
        trader_address = load_trader_client.getnewaddress()

        # Send 20 BTC from Miner to Trader.
        tx_id = miner_client.sendtoaddress(trader_address, 20)
    
        # Check the transaction in the mempool.
        try:
            mempool_tx = check_mempool(client, tx_id)
        except:
            raise(f"an error occured")

        # Mine a block to confirm the transaction
        # block_hash = client.generatetoaddress(1, miner_address)[0]
        client.generatetoaddress(1, miner_address)

        
        # Extract all required transaction details.
        try:
            transaction = get_tx(miner_client, tx_id)
        except Exception as e:
            raise ValueError(f"{e}")
        
        hex = transaction["hex"]
        
        try:
            decoded_tx = decode_raw_tx(miner_client, hex)
        except Exception as e:
            raise ValueError(f"{e}")
        

        prev_tx_id = decoded_tx["vin"][0]["txid"]
        prev_tx_vout = decoded_tx["vin"][0]["vout"]
        try:
            prev_tx = get_tx(miner_client, prev_tx_id)
        except:
            raise ValueError(f"Can't get previous transaction for {prev_tx_id}")


        txid = str(transaction["txid"])
        minerInputAddress = str(prev_tx["details"][prev_tx_vout]["address"])
        minerInputAmount = float(prev_tx["amount"])
        traderInputAddress = str(decoded_tx["vout"][0]["scriptPubKey"]["address"])
        traderInputAmount = float(decoded_tx["vout"][0]["value"])
        minerChangeAddress = str(decoded_tx["vout"][1]["scriptPubKey"]["address"])
        minerChangeAmount = float(decoded_tx["vout"][1]["value"])
        fee = float(transaction["fee"])
        blockHeight = int(transaction["blockheight"])
        blockHash = str(transaction["blockhash"])

        def format_number(num):
            if num == int(num):
                return str(int(num))
            else:
                return str(num)

        with open("out.txt", "w") as f:
            f.write(f"{txid}\n")
            f.write(f"{minerInputAddress}\n")
            f.write(f"{format_number(minerInputAmount)}\n")
            f.write(f"{traderInputAddress}\n")
            f.write(f"{format_number(traderInputAmount)}\n")
            f.write(f"{minerChangeAddress}\n")
            f.write(f"{format_number(minerChangeAmount)}\n")
            f.write(f"{fee}\n")
            f.write(f"{blockHeight}\n")
            f.write(f"{blockHash}")

    except Exception as e:
        print("Error occurred: {}".format(e))

if __name__ == "__main__":
    main()