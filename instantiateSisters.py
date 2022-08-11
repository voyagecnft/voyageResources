import requests
blockfrost_api_key="mainnetnHVXt3qNBLtgIZWfy0h6KT3q7G1WRsx2"
base_api='https://cardano-mainnet.blockfrost.io/api/v0/'
headers={'project_id':f'{blockfrost_api_key}'}

response=requests.get(base_api+"/addresses/"+"0117790b07220e68ecf3889580a0b46f53cf49ec83a3eea357240b963901f2d96bca62eff6ecb0b74e6b4116c2237946784536b9985b343dbe",headers=headers)
print(bytearray.decode(bytearray.fromhex("0117790b07220e68ecf3889580a0b46f53cf49ec83a3eea357240b963901f2d96bca62eff6ecb0b74e6b4116c2237946784536b9985b343dbe")))
print(response.json())