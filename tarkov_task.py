from astrbot.api import logger
from astrbot.api.star import StarTools
import aiohttp
import asyncio
import json
import os
from datetime import datetime



async def scheduled_task(config):
    if(config["item_task"]["item_task_condition"] is True):
        item_task_period = config["item_task"]["item_task_period"]
        asyncio.create_task(item_task(item_task_period))
        
"""
定时查询tarkov-dev API 获取跳蚤价格
传参：  1.period 查询时间周期 从配置表item_task -> item_task_period获取
"""
async def item_task(period):
    url = "https://api.tarkov.dev/graphql"
    query = """
        {
            items(lang: zh) {
                id
                name
                shortName
                avg24hPrice
                basePrice
                lastLowPrice
                wikiLink
                sellFor {
                    price
                    source
                    currency
                }
                buyFor {
                    price
                    source
                    currency
                }
            }
        }
    """
    headers = {"Content-Type": "application/json"}
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.post(url, headers=headers, json={'query': query}) as response:
                    if response.status == 200:
                        item_result = await response.json()
                        # 使用框架标准方法获取插件数据目录
                        data_dir = StarTools.get_data_dir("astrbot_plugin_tarkov")
                        filepath = data_dir / "item.json"
                        await save_task_data(item_result, str(filepath))
                    else:
                        error_text = await response.text()
                        print(f"❌ 请求失败 Code: {response.status}, Error: {error_text}")
            except asyncio.CancelledError:
                print("🛑 任务被取消")
                break
            except Exception as e:
                print(f"⚠️ 发生错误: {e}")
            await asyncio.sleep(period*60)
        

"""
创建+覆盖模式存入data
"""
async def save_task_data(data, filepath):
    # 转换为绝对路径（StarTools.get_data_dir() 已自动创建目录）
    abs_filepath = os.path.abspath(filepath)
    # 记录更新时间
    if isinstance(data, dict):
        data["update_time"] = datetime.now().isoformat(timespec="seconds")
    with open(abs_filepath, 'w', encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    logger.info(f"数据已成功写入 {abs_filepath}")

