import hashlib
import datetime
import json
import pprint
import flask
from flask import request, jsonify

app = flask.Flask(__name__)
app.config['DEBUG'] = True


@app.route('/hello', methods=['GET'])
def home():
    return 'Your web app is running'


class Block:
    def __init__(self, timeStamp, trans, previousBlock=''):
        self.timeStamp = timeStamp
        self.trans = trans
        self.previousBlock = previousBlock
        self.difficultyIncrement = 0
        self.hash = self.calculateHash(trans, timeStamp, self.difficultyIncrement)

    def calculateHash(self, data, timeStamp, difficultyIncrement):
        data = str(data) + str(timeStamp) + str(difficultyIncrement)
        data = data.encode()
        hash = hashlib.sha256(data)
        return hash.hexdigest()

    def mineBlock(self, difficulty):
        difficultyCheck = "9" * difficulty
        while self.hash[:difficulty] != difficultyCheck:
            self.hash = self.calculateHash(self.trans, self.timeStamp, self.difficultyIncrement)
            self.difficultyIncrement = self.difficultyIncrement + 1


class Blockchain:
    def __init__(self):
        self.chain = [self.GenesisBlock()]
        self.difficulty = 5
        self.pendingTransaction = []
        self.reward = 10

    def GenesisBlock(self):
        genesisBlock = Block(str(datetime.datetime.now()), " Gensis Block")
        return genesisBlock

    def getLastBlock(self):
        return self.chain[len(self.chain) - 1]

    def minePendingTrans(self, minerRewardAddress):
        # in reality not all of the pending transaction go into the block the miner gets to pick which one to mine
        newBlock = Block(str(datetime.datetime.now()), self.pendingTransaction)
        newBlock.mineBlock(self.difficulty)
        newBlock.previousBlock = self.getLastBlock().hash

        print("Previous Block's Hash: " + newBlock.previousBlock)
        testChain = []
        for trans in newBlock.trans:
            temp = json.dumps(trans.__dict__, indent=5, separators=(',', ': '))
            testChain.append(temp)
        pprint.pprint(testChain)

        self.chain.append(newBlock)
        print("Block's Hash: " + newBlock.hash)
        print("Block added")

        rewardTrans = Transaction("System", minerRewardAddress, self.reward)
        self.pendingTransaction.append(rewardTrans)
        self.pendingTransaction = []

    def isChainValid(self):
        for x in range(1, len(self.chain)):
            currentBlock = self.chain[x]
            previousBlock = self.chain[x - 1]

            if (currentBlock.previousBlock != previousBlock.hash):
                return ("The Chain is not valid!")
        return ("The Chain is valid and secure")

    def createTrans(self, transaction):
        self.pendingTransaction.append(transaction)

    @app.route('/name/balance', methods=['GET', 'POST'])
    def getBalance(self):
        if request.method == 'POST':
            walletAddress = request.form['name']
        balance = 0
        for block in self.chain:
            if block.previousBlock == "":
                # dont check the first block
                continue
            for transaction in block.trans:
                if transaction.fromWallet == walletAddress:
                    balance -= transaction.amount
                if transaction.toWallet == walletAddress:
                    balance += transaction.amount
        return jsonify(balance)


class Transaction:
    def __init__(self, fromWallet, toWallet, amount):
        self.fromWallet = fromWallet
        self.toWallet = toWallet
        self.amount = amount

@app.route('/buy',methods=['GET','POST'])
def buy(name, price):

    solariCrypto.createTrans(Transaction(name, "SpaceBrokers", price))

@app.route('/mine',methods=['GET','POST'])
def mine():
    if request.method == 'POST':
        walletAddress = request.form['name']
        solariCrypto.minePendingTrans(walletAddress)


solariCrypto = Blockchain()

if __name__ == '__main__':
    app.run()
