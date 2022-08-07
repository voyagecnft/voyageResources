import datetime
import time
now=datetime.datetime.now()
print(now)
now=now.isoformat()
print(now)

earlierDate=datetime.datetime.fromisoformat(now)

print((datetime.datetime.now()-earlierDate).day())