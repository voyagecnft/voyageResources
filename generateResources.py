import os,json
import requests

# 4 tables, one for each resource
# if tables absent, add tables

# flow 
# get assets, hashmap for stake key to planets, continents and floating continents -
# iterate over all assets 
# if planet - check for multiplier 
# add resource for each asset 
# print a log file tracking assets for each stake address



def fetchAssets(Policies):
    with open('blockfrostKey.txt','r') as f:
        key=f.read()
        f.close()
    
    Assets=[] # array of dics , plaintext name : policy+hexname

    def addAssetsOfPolicyID(Assets,policyID,key):
        blockfrost_api_key=key
        project_policy_id=policyID

        base_api='https://cardano-mainnet.blockfrost.io/api/v0/'
        headers={'project_id':f'{blockfrost_api_key}'}
        page=1

        while True:
            response=requests.get(f'{base_api}/assets/policy/{project_policy_id}?page={page}',headers=headers)
            if len(response.json())==0:
                break
            for asset in response.json():
                temp={}
                asset_hex_name=asset["asset"][len(project_policy_id):]
                temp["name"]=bytearray.decode(bytearray.fromhex(asset_hex_name))
                temp["asset"]=asset["asset"]
                Assets.append(temp)
            page+=1
            print(f"{policyID} {page}")


    for policyID in Policies:
        addAssetsOfPolicyID(Assets,policyID,key)
    
    stakeToAssetMap={}
    



if __name__=="__main__":
    stakeToAssetMap=fetchAssets(["7371b76a7cfb71c5c70618fd2b27f357a6eb84c38ad4f92fed1164f2","0799a79aefe81aeb718e75982c26e1719d94fe75860b3ba184971428"])

