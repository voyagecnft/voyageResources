import os,json


# 4 tables, one for each resource
# if tables absent, add tables

# flow 
# get assets, hashmap for stake key to planets, continents and floating continents -
# iterate over all assets 
# if planet - check for multiplier 
# add resource for each asset 
# print a log file tracking assets for each stake address

def getSisters(assetName,resourceType):
    with open(f'planetMetadata/{planet}.metadata','r') as f:
       
        data=json.load(f)
        f.close()
        return data['721']['<policy_id>'][planet]['sisterPlanets']





if __name__=="__main__":
    