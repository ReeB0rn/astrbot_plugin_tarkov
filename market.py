from dataclasses import dataclass, field
from typing import List, Optional
import os
import json
import asyncio
from astrbot.api.star import StarTools
from astrbot.api import logger

@dataclass
class Offer:
    """单个交易来源信息（sellFor / buyFor 中的对象）"""
    price: Optional[int] = None
    source: Optional[str] = None
    currency: Optional[str] = None


@dataclass
class Item:
    """表示从 tarkov.dev graphql `items` 返回的单个物品信息"""
    id: str
    name: str
    short_name: Optional[str] = None
    avg_24h_price: Optional[int] = None
    base_price: Optional[int] = None
    last_low_price: Optional[int] = None
    wiki_link: Optional[str] = None
    sell_for: List[Offer] = field(default_factory=list)
    buy_for: List[Offer] = field(default_factory=list)

    @staticmethod
    def from_api(data: dict) -> "Item":
        """根据 API 返回的字典（camelCase 字段）构造 Item 实例"""
        def _to_offer_list(offers):
            if not offers:
                return []
            return [
                Offer(
                    price=offer.get("price"),
                    source=offer.get("source"),
                    currency=offer.get("currency"),
                )
                for offer in offers
            ]

        return Item(
            id=str(data.get("id", "") if data.get("id", "") is not None else ""),
            name=data.get("name", "") or "",
            short_name=data.get("shortName"),
            avg_24h_price=data.get("avg24hPrice"),
            base_price=data.get("basePrice"),
            last_low_price=data.get("lastLowPrice"),
            wiki_link=data.get("wikiLink"),
            sell_for=_to_offer_list(data.get("sellFor")),
            buy_for=_to_offer_list(data.get("buyFor")),
        )

async def get_item_info(name: str) -> str:
    """根据物品名称模糊查询物品信息，返回便于阅读的字符串（可能为空匹配提示）"""
    # 检查 data 目录下的 item.json 是否存在且非空
    data_dir = StarTools.get_data_dir("astrbot_plugin_tarkov")
    filepath = data_dir / "item.json"
    filepath_str = str(filepath)

    if not os.path.exists(filepath_str) or os.path.getsize(filepath_str) == 0:
        raise FileNotFoundError(f"item.json 未找到或为空: {filepath_str}")

    # 使用线程读取文件以避免阻塞事件循环
    def _load_file():
        with open(filepath_str, "r", encoding="utf-8") as f:
            return json.load(f)

    data = await asyncio.to_thread(_load_file)

    # 解析可能的结构：{"data": {"items": [...]}} 或 {"items": [...]} 或 [...]
    items_list = None
    if isinstance(data, dict):
        if "data" in data and isinstance(data["data"], dict) and "items" in data["data"]:
            items_list = data["data"]["items"]
        elif "items" in data:
            items_list = data["items"]
    elif isinstance(data, list):
        items_list = data

    if not items_list:
        raise ValueError(f"item.json 中未找到 items 列表: {filepath_str}")

    q = name.strip().lower()
    # 收集匹配结果，避免重复（使用 id 去重）
    exact_matches: List[Item] = []
    fuzzy_matches: List[Item] = []
    seen_ids = set()

    # 优先精确匹配（不区分大小写）
    for entry in items_list:
        entry_id = entry.get("id")
        entry_name = (entry.get("name") or "").lower()
        entry_short = (entry.get("shortName") or "").lower()
        if entry_name == q or entry_short == q:
            item_obj = Item.from_api(entry)
            exact_matches.append(item_obj)
            if entry_id:
                seen_ids.add(entry_id)

    # 然后进行子串模糊匹配（不区分大小写），补充未命中的项
    for entry in items_list:
        entry_id = entry.get("id")
        if entry_id in seen_ids:
            continue
        entry_name = (entry.get("name") or "").lower()
        entry_short = (entry.get("shortName") or "").lower()
        if q in entry_name or q in entry_short:
            item_obj = Item.from_api(entry)
            fuzzy_matches.append(item_obj)
            if entry_id:
                seen_ids.add(entry_id)

    results = exact_matches + fuzzy_matches

    if not results:
        return f"未找到与 \"{name}\" 匹配的物品。"

    # 构建按照用户指定格式的可读字符串
    lines: List[str] = []
    for it in results:
        lines.append(f"物品名称：{it.name}")
        lines.append(f"跳蚤24小时平均价格：{it.avg_24h_price if it.avg_24h_price is not None else '-'}")
        lines.append(f"基础价格：{it.base_price if it.base_price is not None else '-'}")
        lines.append(f"跳蚤最低价格：{it.last_low_price if it.last_low_price is not None else '-'}")
        # 可卖给（sell_for）
        lines.append("可卖给：")
        if it.sell_for:
            for offer in it.sell_for:
                src = offer.source or "-"
                price = offer.price if offer.price is not None else "-"
                curr = offer.currency or ""
                lines.append(f"        {src} {price}{curr}")
        else:
            lines.append("        -")

        # 购买渠道（buy_for）
        lines.append("购买渠道：")
        if it.buy_for:
            for offer in it.buy_for:
                src = offer.source or "-"
                price = offer.price if offer.price is not None else "-"
                curr = offer.currency or ""
                lines.append(f"        {src} {price}{curr}")
        else:
            lines.append("        -")

        # wiki 链接
        lines.append(f"wiki链接：{it.wiki_link or '-'}")
        # 分隔空行
        lines.append(f"更新时间：{data['update_time']}")
        lines.append("")

    return "\n".join(lines).rstrip()