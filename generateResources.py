import os,json


# 4 tables, one for each resource
# if tables absent, add tables

# flow 
# get assets, hashmap for stake key to planets, continents and floating continents -
# iterate over all assets 
# if planet - check for multiplier 
# add resource for each asset 
# print a log file tracking assets for each stake address


def fetchAssets():
    with open('blockfrostKey.txt','r') as f:
        key=f.read()
        f.close()
    




if __name__=="__main__":
    stakeToAssetMap=fetchAssets()