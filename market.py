from astrbot.api import logger
import httpx


async def scheduled_task(config):
    if(config["item_task"]["item_task_condition"] is True):
        item_task_period = config["item_task"]["item_task_period"]
        aysncio.create_task(item_task(item_task_period))
        
"""
定时查询tarkov-dev API 获取跳蚤价格
传参：  1.period 查询时间周期 从配置表item_task -> item_task_period获取
"""
async def item_task(period):
    while True:
        print(f"物品跳蚤查询定时任务开启，查询周期为{period}")

         """
        向 Tarkov.dev API 发送请求获取物品信息
        :param name: 物品名称 (例如: "M4A1", "Red Keycard")
        :return: 物品列表或 None
        """
        url = "https://api.tarkov.dev/graphql"

        query = """
        query GetItem($name: String!) {
            items(name: $name lang: zh) {
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
        # TODO 请求写入文件
        try:
            # 使用异步上下文管理器创建 client
            async with httpx.AsyncClient() as client:
                payload = {
                    "query": query,
                    "variables": {"name": name}
                }
                # 发送 POST 请求
                response = await client.post(url, json=payload, timeout=10.0)

                if response.status_code == 200:
                    result = response.json()
                    
                else:
                    logger.error(f"Tarkov API 请求失败: HTTP {response.status_code}")
        except Exception as e:
            logger.error(f"Tarkov API 请求异常: {e}")
        await asyncio.sleep(period*60)

    