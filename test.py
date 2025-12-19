import requests
import json

def fetch_all_tasks():
    url = "https://api.tarkov.dev/graphql"
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # 已改回 lang: zh
    query = """
    query TarkovDevTasks {
      tasks(lang: zh, gameMode: regular) {
        id
        tarkovDataId
        name
        normalizedName
        trader { id name normalizedName }
        map { id name normalizedName }
        experience
        wikiLink
        minPlayerLevel
        taskRequirements { task { id } status }
        traderRequirements { trader { id name } requirementType compareMethod value }
        restartable
        objectives { ...TaskObjectiveInfo }
        failConditions { ...TaskObjectiveInfo }
        startRewards { ...taskRewardFragment }
        finishRewards { ...taskRewardFragment }
        failureOutcome { ...taskRewardFragment }
        factionName
        neededKeys { keys { id } map { id } }
        kappaRequired
        lightkeeperRequired
        taskImageLink
      }
      achievements(lang: zh) {
        id name description hidden playersCompletedPercent
        adjustedPlayersCompletedPercent normalizedRarity rarity imageLink
      }
      prestige(lang: zh, gameMode: regular) {
        id name prestigeLevel imageLink iconLink
        conditions { ...TaskObjectiveInfo }
        rewards { ...taskRewardFragment }
        transferSettings {
          ...on PrestigeTransferSettingsSkill { name skillType transferRate }
          ...on PrestigeTransferSettingsStash {
            gridWidth gridHeight
            itemFilters {
              allowedCategories { id } allowedItems { id }
              excludedCategories { id } excludedItems { id }
            }
          }
        }
      }
    }

    fragment TaskObjectiveInfo on TaskObjective {
      __typename id type description maps { id name } optional
      ...on TaskObjectiveBasic { zones { id map { id } position { x y z } outline { x y z } top bottom } }
      ...on TaskObjectiveBuildItem { item { id } containsAll { id } containsCategory { id name normalizedName } attributes { name requirement { compareMethod value } } }
      ...on TaskObjectiveExperience { healthEffect { bodyParts effects time { compareMethod value } } }
      ...on TaskObjectiveExtract { exitStatus exitName count }
      ...on TaskObjectiveHideoutStation { hideoutStation { id } stationLevel }
      ...on TaskObjectiveItem { items { id } count foundInRaid dogTagLevel maxDurability minDurability zones { id map { id } position { x y z } outline { x y z } top bottom } }
      ...on TaskObjectiveMark { markerItem { id } zones { id map { id } position { x y z } outline { x y z } top bottom } }
      ...on TaskObjectivePlayerLevel { playerLevel }
      ...on TaskObjectiveQuestItem { questItem { id name shortName width height iconLink image512pxLink baseImageLink image8xLink } possibleLocations { map { id } positions { x y z } } zones { id map { id } position { x y z } outline { x y z } top bottom } count }
      ...on TaskObjectiveShoot { targetNames count shotType zoneNames bodyParts timeFromHour timeUntilHour usingWeapon { id } usingWeaponMods { id } wearing { id } notWearing { id } distance { compareMethod value } playerHealthEffect { bodyParts effects time { compareMethod value } } enemyHealthEffect { bodyParts effects time { compareMethod value } } zones { id map { id } position { x y z } outline { x y z } top bottom } }
      ...on TaskObjectiveSkill { skillLevel { level skill { id } } }
      ...on TaskObjectiveTaskStatus { task { id } status }
      ...on TaskObjectiveTraderLevel { trader { id } level }
      ...on TaskObjectiveTraderStanding { trader { id } compareMethod value }
      ...on TaskObjectiveUseItem { useAny { id } compareMethod count zoneNames zones { id map { id } position { x y z } outline { x y z } top bottom } }
    }

    fragment cutomizationRewardFragment on CustomizationItem {
      id name customizationType customizationTypeName imageLink
      ...on CustomizationItems { items { id } }
    }

    fragment taskRewardFragment on TaskRewards {
      traderStanding { trader { id } standing }
      items { item { id containsItems { item { id } count } } count attributes { name value } }
      offerUnlock { trader { id } level item { id } }
      craftUnlock { id station { id } level rewardItems { item { id } count } }
      skillLevelReward { name level }
      traderUnlock { id }
      achievement { id }
      customization { ...cutomizationRewardFragment }
    }
    """

    try:
        response = requests.post(url, json={'query': query}, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            return None
    except Exception as e:
        print(e)
        return None

# 执行
data = fetch_all_tasks()
if data and 'data' in data:
    print(f"{data}")
    print(f"成功获取数据！共 {len(data['data']['tasks'])} 个任务")