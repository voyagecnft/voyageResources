import os,json
import requests
import csv
import datetime
import time
import math
# 4 tables, one for each resource
# if tables absent, add tables

# flow 
# get assets, hashmap for stake key to planets, continents and floating continents -
# iterate over all assets 
# if planet - check for multiplier 
# add resource for each asset 
# print a log file tracking assets for each stake address
maximum=[] # for debugging


def fetchAssets(Policies):
    with open('blockfrostKey.txt','r') as f:
        key=f.read()
        f.close()
    base_api='https://cardano-mainnet.blockfrost.io/api/v0/'
    blockfrost_api_key=key
    
    headers={'project_id':f'{blockfrost_api_key}'}
    Assets=[] # array of dics , plaintext name : policy+hexname

    def addAssetsOfPolicyID(Assets,policyID,key):
        blockfrost_api_key=key
        project_policy_id=policyID

        base_api='https://cardano-mainnet.blockfrost.io/api/v0/'
        headers={'project_id':f'{blockfrost_api_key}'}
        page=1

        while True:
            response=requests.get(f'{base_api}/assets/policy/{project_policy_id}?page={page}',headers=headers)
            #time.sleep(0.5)
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
    stakeDict={} # saving api calls mapping used address to stake address , DP
    # mapping to stake key

    for asset in Assets:
        response=requests.get(f'{base_api}/assets/{asset["asset"]}/addresses',headers=headers)
        #time.sleep(0.5)
        address=response.json()[0]['address']
        # used address
        
        if address in stakeDict:
            stakeAddress=stakeDict[address]
        else:
            stakeAddress=requests.get(f'{base_api}/addresses/{address}',headers=headers).json()["stake_address"]
            #time.sleep(0.5)
        print(asset["name"])
        if stakeAddress not in stakeToAssetMap:
            stakeToAssetMap[stakeAddress]=[]
        stakeToAssetMap[stakeAddress].append(asset["name"])
        #break # temporary for debugging 
    return stakeToAssetMap

def sisterMultiplier(asset,assets,metadata):
    global maximum
    sisters=metadata['sisterPlanets']
    if sisters=="none":
        return 1
    n=len(sisters)+1
    
    common= len(list(set(assets)&set(sisters)))+1

    
    
    
    return 1


def computeResources(stakeAddress,asset,assets,resource):
    if asset=="1503":
        return 0
     # compute a particular resource farmed from a particular asset for a particular stake address
    
    if "floating" in asset:
        path="floating"
    elif "continent" in asset:
        path="continent"
    else:
        path="planet"
    
    with open(f'{path}Metadata/{asset}.metadata','r') as f:
        metadata=json.load(f)["721"]["<policy_id>"][asset]
    
    if resource not in metadata: # case of continent
        temp=0
    elif "floating" in asset:
        temp=2*metadata[resource]
    elif "continent" in asset:
        temp=0.95*metadata["production rate"]
    else: # planet
        tier=metadata['Tier']
        if tier=='A':
            c=3
        elif tier=='B':
            c=2
        else:
            c=1
        temp=c*metadata[resource]
        temp=temp*sisterMultiplier(asset,assets,metadata)
        
    
    return math.floor(temp)


def calculateRewards(inputFile):
    # open existing file and check current rewards
    resources=["Elixir","Rock","Crystal","Antimatter"]
    files=os.listdir('.')

    data={} # info to be written // dic of dics
   
    with open(inputFile,"r") as csv_file:
        csv_reader=csv.reader(csv_file,delimiter=',')
        i=0
        j=0
        for row in csv_reader: # iterating over all stake addresses
            
            stakeAddress=row[0]
            assets=row[1].split(" ")
            data[stakeAddress]={}

            # update rewards if >= 7 days from previous update else don't do anything and print rewards were not updated
            # first row should be the date when it is updated
            earnedResources={} # resources earned by a particular stake address
            for resource in resources:
                earnedResources[resource]=0

            # for each asset, compute each resource one by one
            for asset in assets:
                for resource in resources:
                    temp=computeResources(stakeAddress,asset,assets,resource)

    
            

def printLogs(stakeToAssetMap):
    data=[]
    for stakeAddress in stakeToAssetMap:
        data.append([stakeAddress," ".join(stakeToAssetMap[stakeAddress]),datetime.datetime.now()])
    file=open('logs.csv','w')
    csvWriter=csv.writer(file,delimiter=',')
    csvWriter.writerows(data)
    file.close()


if __name__=="__main__":
    d=input("take new snapshot ? ")
    if d=="yes":
        stakeToAssetMap=fetchAssets(["7371b76a7cfb71c5c70618fd2b27f357a6eb84c38ad4f92fed1164f2","0799a79aefe81aeb718e75982c26e1719d94fe75860b3ba184971428"])

        # print out logs 
        printLogs(stakeToAssetMap)

    calculateRewards("logs.csv")

    
