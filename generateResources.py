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
            if len(response.json())==0: # assets of particular policy have been exhausted
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
            stakeDict[address]=stakeAddress
            #   time.sleep(0.5)
        print(asset["name"])
        if stakeAddress not in stakeToAssetMap:
            stakeToAssetMap[stakeAddress]=[]
        stakeToAssetMap[stakeAddress].append(asset["name"])
        #break # temporary for debugging 
    return stakeToAssetMap

def sisterMultiplier(asset,assets,metadata):
    
    sisters=metadata['sisterPlanets']
    if sisters=="none":
        return 1
    n=len(sisters)+1 # total set size
    
    common= len(list(set(assets)&set(sisters)))+1 # set intersection

    k=1
    if common>=13:
        k=2.5
    elif common>=10:
        k=2
    elif common>=7:
        k=1.8
    elif common>=4:
        k=1.5
    elif common>=2:
        k=1.3
    
    kOptions=[1.3,1.5,1.8,2,2.5]

    if common==n: # not possible in case k=1
        # full set extra boost
        i=kOptions.index(k)
        i=min(i+1,len(kOptions)-1)
        k=kOptions[i]
    
    
    return k


def computeResources(stakeAddress,asset,assets,resource):
    if asset=="1503": # wrongly minted assed
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
    
    if "floating" in asset: #floating continent
        if resource!=metadata['resource']:
            temp=0
        else:
            temp=2*int(metadata["productionRate"])
    elif "continent" in asset: # continent
        if resource!=metadata['resource']:
            temp=0
        else:
            temp=0.95*float(metadata["production rate"])
    else: # planet
        #print(asset)
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
    data={} # info to be written // dic of dics
   
    with open(inputFile,"r") as csv_file:
        csv_reader=csv.reader(csv_file,delimiter=',')
        for row in csv_reader: # iterating over all stake addresses
            stakeAddress=row[0]
            assets=row[1].split(" ")
            data[stakeAddress]={}

    
            earnedResources={} #each resource earned by a particular stake address
            for resource in resources:
                earnedResources[resource]=0

            # for each asset, compute each resource one by one
            for asset in assets:
                for resource in resources:
                    temp=computeResources(stakeAddress,asset,assets,resource) 
                    earnedResources[resource]+=temp # add resource from this asset to the stakeAddress wallet
            data[stakeAddress]=earnedResources
    #print(data)
    return data # {stakeKey1 : {resource 1:val, resoure2:val ........}, stakekey2: ........}
                
def updateRewards(data):
    """
    resource file
    first line date
    stake address to resource file
    
    """
    curFiles=os.listdir('.')
    
    for resource in ["Elixir","Antimatter","Crystal","Rock"]:
        
        curData= {}
        for stake in data:
            if stake!="": # excluding last line from logs file
                curData[stake]=data[stake][resource]
        
        
        if f'{resource}.csv' in curFiles: # previous record exists
            with open(f"{resource}.csv","r") as f:
                csv_reader=csv.reader(f,delimiter=',')
                prevDate=""
                for row in csv_reader: # only need to check the first row for date 
                    prevDate=datetime.datetime.fromisoformat(row[0])
                    
                    break
                f.close()
                delta=datetime.datetime.now()-prevDate
                if delta <= datetime.timedelta(days=7):
                    print(f"last {resource}  update less than 7 days ago ")
                # if there has been more than less than 7 days , write it has been less than 7 days since updation and exit
                else:
                    print(f"{resource} updated!")

                    f=open(f'{resource}.csv',"r")
                    prevData={}
                    csv_reader=csv.reader(f,delimiter=",")
                    for row in csv_reader:
                        if "stake" in row[0]: # ignoring the first row containing date information
                            prevData[row[0]]=float(row[1])
                    
                    f.close()

                    f=open(f'{resource}.csv',"w")
                    csvWriter=csv.writer(f,delimiter=",")
                    csvWriter.writerow([datetime.datetime.now().isoformat()]*2)
                    for stakeAddress in prevData:
                        if stakeAddress in curData: # present in both weeks
                            csvWriter.writerow([stakeAddress,prevData[stakeAddress]+float(curData[stakeAddress])])
                        else: # only present in prev week
                            csvWriter.writerow([stakeAddress,prevData[stakeAddress]])
                    for stakeAddress in curData: # only present in curWeek
                        if stakeAddress not in prevData:
                            csvWriter.writerow([stakeAddress,curData[stakeAddress]])
                    
                    


                
                
        else:
            
            f=open(f'{resource}.csv',"w")
            csvWriter=csv.writer(f,delimiter=",")
            csvWriter.writerow([datetime.datetime.now().isoformat()]*2)
            for stakeAddress in curData:
                csvWriter.writerow([stakeAddress,curData[stakeAddress]])
            f.close()

            print(f"{resource} added!")
            




    
            

def printLogs(stakeToAssetMap):
    data=[]
    for stakeAddress in stakeToAssetMap:
        data.append([stakeAddress," ".join(stakeToAssetMap[stakeAddress]),datetime.datetime.now().isoformat()])
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

    data=calculateRewards("logs.csv")
    
    # adding rewards to existing logs
    
    updateRewards(data)

    # uploading to aws 

    for file in ["Antimatter.csv","Crystal.csv","Elixir.csv","logs.csv","Rock.csv"]:
        os.system(f'aws s3 cp {file} s3://www.cnftvoyage.com/resourceData/')    






