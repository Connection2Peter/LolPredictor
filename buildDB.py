# -*- coding: utf-8 -*-
import os, sys, csv, time
from datetime import datetime
from riotwatcher import LolWatcher, ApiError

### Setting
RequireArgs = [ "{Riot Name}", "{Region}", "{output folder}", "{Riot Api Key}"]
if len(sys.argv) < len(RequireArgs) + 1:
    print("### Usage")
    print("# python", sys.argv[0], " ".join(RequireArgs))
    print("### Example")
    print("# python", sys.argv[0], "Ironmin136 kr db RGAPI-df092290-fa66-499b-926b-32a860c34518")

    exit("\n### End ###\n")

player = sys.argv[1]
region = sys.argv[2]
output = sys.argv[3]
apiKey = sys.argv[4]

""" 資料格式
**Target:**
0. Win or not (Win=1, Lose=2)

**Feature:**
1. 己方玩家總勝率(*5)
2. 對方玩家總勝率(*5)
3. 己方角色編碼(*5)
4. 對方角色編碼(*5)
7. 對局時段(以一小時為單位)
"""

limit = 100
before = 0
timeNow = time.strftime("%Y-%m-%d_%H-%M-%S_", time.localtime())
optName = os.path.join(output, timeNow + player + ".csv")
Watcher = LolWatcher(apiKey)
UserInfo = Watcher.summoner.by_name(region, player)

with open(optName, 'w', encoding='utf-8-sig', newline='') as fout:
    CsvWriter = csv.writer(fout)

    while True:
        try:
            UserGames = Watcher.match.matchlist_by_puuid(region, UserInfo['puuid'], start=before, count=limit)
        except:
            break

        for game in UserGames:
            time.sleep(0.5)

            try:
                GameData = Watcher.match.by_id(region, game)
            except:
                continue

            if GameData['info']['gameMode'] != 'CLASSIC':
                continue

            try:
                timeStamp = datetime.fromtimestamp(GameData["info"]["gameStartTimestamp"] / 1000.0)
            except:
                continue

            userTeamID = 0
            userWinLose = 0
            unSortDatas = []

            for participant in GameData["info"]["participants"]:
                unSortDatas.append([participant["teamId"], participant["puuid"], participant["championId"],])
    
                if participant["puuid"] == UserInfo['puuid']:
                    userTeamID = participant["teamId"]
    
                if participant["win"] == True:
                    userWinLose = 1
                else:
                    userWinLose = 2

            userTeamWinRate, nonUserTeamWinRate, userTeamCid, nonUserTeamCid = [], [], [], []

            for i in unSortDatas:
                SummonerInfo = Watcher.summoner.by_puuid(region, i[1])

                time.sleep(0.5)

                LeagueInfo = Watcher.league.by_summoner(region, SummonerInfo['id'])

                if len(LeagueInfo) < 1:
                    continue

                try:
                    winRate = round(LeagueInfo[0]['wins'] / (LeagueInfo[0]['wins'] + LeagueInfo[0]['losses']), 8)
                except:
                    continue

                if i[0] == userTeamID:
                    userTeamWinRate.append(winRate)
                    userTeamCid.append(i[2])
                else:
                    nonUserTeamWinRate.append(winRate)
                    nonUserTeamCid.append(i[2])

                time.sleep(0.5)

            singleElement = [userWinLose, timeStamp.hour] + userTeamWinRate + nonUserTeamWinRate + userTeamCid + nonUserTeamCid

            if userWinLose == 0 or len(singleElement) != 22:
                continue

            print("#", timeStamp)
            print(singleElement)
            CsvWriter.writerow([float(i) for i in singleElement])
        before += limit

print("### Done !!!")
