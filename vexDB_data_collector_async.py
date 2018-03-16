#!/usr/local/bin/python3.6
# -*- coding:utf-8 -*-

import requests,json,os,datetime,sys,itertools,asyncio,aiohttp,html
if len(sys.argv)==1:
    event_sku= "RE-VRC-17-3805"
else:
    event_sku=sys.argv[1]
sys.stdout.write("Gathering initial information.")
sys.stdout.flush()
event=json.loads(requests.get("https://api.vexdb.io/v1/get_events?sku=" + event_sku).content)
sys.stdout.write('.')
if event['size']==0:
    sys.stdout.write("\nEvent with SKU %s not found. Exit.\n" % event_sku)
    sys.exit(0)
event_name=event['result'][0]['name']
teams = json.loads(requests.get("https://api.vexdb.io/v1/get_teams?sku=" + event_sku).content)
sys.stdout.write('.')
if teams['size']==0:
    sys.stdout.write('\nTeam list for event "%s" is empty. Exit.\n'%event_name)
    sys.exit(0)
if len(sys.argv)==3:
    path=os.path.expanduser(sys.argv[2])
else:
    path=os.path.join(os.path.dirname(os.path.abspath(__file__)),event_name+' Data.csv')
sys.stdout.write("done")
sys.stdout.flush()
f=open(path,"w+")
f.write("Team Number,Team Name,Organization,Region,Country,Autonomous Skill,Autonomous Rank,Driver Skill,Driver Rank,Combined Skills,Skill Rank,vRating,vRating Rank,Highest Match Score,Highest Score Alliance, Most Recent Event Average\n")
skus={}
#for i,team in enumerate(res['result']):
loop=asyncio.get_event_loop()
conn=aiohttp.TCPConnector(ssl=True)
session=aiohttp.ClientSession(loop=loop,connector=conn)
i=0

async def get_team_data(team,client:aiohttp.ClientSession):
    #print("Processing Team","%d/%d"%(i+1,res["size"]))
    global i
    team_number=team["number"]
    season_rankings=await client.get("http://api.vexdb.io/v1/get_season_rankings?season=current&team=" + team_number)
    season_rankings=await season_rankings.read()
    season_rankings=json.loads(season_rankings.decode('utf-8'))
    skills=await client.get("https://api.vexdb.io/v1/get_skills?season_rank=true&season=current&team="+team_number)
    skills=json.loads((await skills.read()).decode('utf-8'))
    sr,combined,auton_score,auton_rank,driver_score,driver_rank=itertools.repeat('N/A',6)
    for s in skills["result"]:
        if s["type"]==2: sr,combined=s['season_rank'],s['score']
        elif s["type"]==1:auton_score,auton_rank=s["score"],s["season_rank"]
        else:driver_score,driver_rank=s["score"],s["season_rank"]
    vrating,vrating_rank=season_rankings["result"][0]["vrating"],season_rankings["result"][0]["vrating_rank"]
    matches=await client.get("https://api.vexdb.io/v1/get_matches?season=current&team="+team["number"])
    matches=json.loads((await matches.read()).decode('utf-8'))
    scores={}
    for m in filter(lambda d: d["scored"],matches['result']):
        sku=m['sku']
        if not sku in skus:
            d=await client.get("https://api.vexdb.io/v1/get_events?sku="+sku)
            skus[sku]=json.loads((await d.read()).decode('utf-8'))['result'][0]
            skus[sku]['time']=datetime.date(*map(int,skus[sku]['start'][:10].split('-')))
        if sku in scores:
            scores[sku].append(m["bluescore"] if team_number in (m["blue1"],m["blue2"],m["blue3"]) else m["redscore"])
        else:
            scores[sku]=[m["bluescore"] if team_number in (m["blue1"],m["blue2"],m["blue3"]) else m["redscore"]]
    most_recent=max(scores.items(),key=lambda s: skus[s[0]]['time'])
    highest_match=max(filter(lambda d: d["scored"],matches["result"]),key=lambda d: d["bluescore"] if team_number in (d["blue1"],d["blue2"],d["blue3"]) else d["redscore"])
    al1,al2,al3=(highest_match["blue1"],highest_match["blue2"],highest_match["blue3"]) if team_number in (highest_match["blue1"],highest_match["blue2"],highest_match["blue3"]) else (highest_match["red1"],highest_match["red2"],highest_match["red3"])
    f.write(html.unescape("{number},{name},{org},{region},{country},{auton},{auton_rank},{driver},{driver_rank},{combined},{sr},{vrating},{vrank},{hms},{hma},{avg}\n".format(
            number=team['number'],
            name=team["team_name"],
            org=team["organisation"],
            sr=sr,
            auton_rank=auton_rank,
            driver=driver_score,
            auton=auton_score,
            combined=combined,
            driver_rank=driver_rank,
            vrating=vrating,
            vrank=vrating_rank,
            hms=highest_match["bluescore"] if team_number in (highest_match["blue1"],highest_match["blue2"],highest_match["blue3"]) else highest_match["redscore"],
            hma=("%s%s%s"%(al1,al2,al3)).replace(team_number,"").replace(highest_match["bluesit"] if team_number in (highest_match["blue1"],highest_match["blue2"],highest_match["blue3"]) else highest_match["redsit"],""),
            region=team["region"],
            country=team["country"],
            avg=sum(most_recent[1])/len(most_recent[1])
    )))
    i+=1
    sys.stdout.write('\rFinished processing team %d/%d'%(i,teams['size']))
    sys.stdout.flush()
    if i==teams['size']:loop.stop()


sys.stdout.write('\nBegin processing data for %s\n'%event_name)
for team in teams['result']:
    asyncio.ensure_future(get_team_data(team,session),loop=loop)
try:
    loop.run_forever()
finally:
    conn.close()
    loop.close()
    f.close()
    sys.stdout.write('\nOutput file saved to "%s". Exit.\n'%path)
