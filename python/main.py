from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from decimal import Decimal
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
    


def get_raw_tx(client, tx_id):
    try:
        tx_details = client.getrawtransaction(tx_id, True)
        return tx_details
    except:
        raise ValueError(f"Can't get taw transaction for {tx_id}")

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

        # load_trader_wallet = create_wallet(client, "Trader")
        load_trader_client = AuthServiceProxy(f"{RPC_URL}/wallet/{trader_wallet}")
        trader_address = load_trader_client.getnewaddress()
        # Send 20 BTC from Miner to Trader.

        tx_id = miner_client.sendtoaddress(trader_address, 20)
        # Check the transaction in the mempool.

        try:
            mempool_tx = check_mempool(client, tx_id)
        except:
            raise(f"an error occured")

        client.generatetoaddress(1, miner_address)

        # Extract all required transaction details.
        try:
            raw_tx = get_raw_tx(client, tx_id)
        except:
            raise ValueError(f"Cant get transaction for {tx_id}")
        

        prev_tx_id = raw_tx["vin"][0]["txid"]
        prev_tx_vout = raw_tx["vin"][0]["vout"]
        try:
            prev_tx = get_raw_tx(client, prev_tx_id)
        except:
            raise ValueError(f"Can't get previous transaction for {prev_tx_id}")

        txid = raw_tx["txid"]
        minerInputAmount = str(prev_tx["vout"][int(prev_tx_vout)]["value"])
        traderInputAmount = str(raw_tx["vout"][0]["value"])
        minerChangeAmount = str(raw_tx["vout"][1]["value"])
        fee = str(Decimal(minerInputAmount) - (Decimal(traderInputAmount) + Decimal(minerChangeAmount)))

        txid = raw_tx["txid"]
        minerInputAddress = prev_tx["vout"][int(prev_tx_vout)]["scriptPubKey"]["address"]
        traderInputAddress = raw_tx["vout"][0]["scriptPubKey"]["address"]
        minerChangeAddress = raw_tx["vout"][1]["scriptPubKey"]["address"]
        blockHash = raw_tx["blockhash"]
        block_info = client.getblock(blockHash)
        blockHeight = block_info["height"]

        # Write the data to ../out.txt in the specified format given in readme.md.
        with open("../out.txt", "w") as f:
            f.write(txid + "\n")
            f.write(minerInputAddress + "\n")
            f.write(minerInputAmount + "\n")
            f.write(traderInputAddress + "\n")
            f.write(traderInputAmount + "\n")
            f.write(minerChangeAddress + "\n")
            f.write(minerChangeAmount + "\n")
            f.write(fee + "\n")
            f.write(str(blockHeight) + "\n")
            f.write(blockHash + "\n")
    except Exception as e:
        print("Error occurred: {}".format(e))

if __name__ == "__main__":
    main()
