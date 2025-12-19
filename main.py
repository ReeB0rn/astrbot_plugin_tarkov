from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import AstrBotConfig
from astrbot.api import logger
from . import market

@register("tarkov", "ReBorn", "塔科夫插件", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context,config: AstrBotConfig):
        super().__init__(context)
        # 获取配置文件 获取失败则为空
        print("初始化成功！")
        self.config = config or {}
        print(self.config)

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
        config = self.config
        await market.scheduled_task(config);

    # 注册指令的装饰器。指令名为 helloworld。注册成功后，发送 `/helloworld` 就会触发这个指令，并回复 `你好, {user_name}!`
    @filter.command("helloworld")
    async def helloworld(self, event: AstrMessageEvent):
        """TODO TARKOV插件DEMO""" # 这是 handler 的描述，将会被解析方便用户了解插件内容。建议填写。
        user_name = event.get_sender_name()
        message_str = event.message_str # 用户发的纯文本消息字符串
        message_chain = event.get_messages() # 用户所发的消息的消息链 # from astrbot.api.message_components import *
        logger.info(message_chain)
        yield event.plain_result(f"Hello!, {user_name}, 你发了 {message_str}!") # 发送一条纯文本消息
    
    @filter.command_group("市场")
    def market(self):
        """跳蚤市场相关指令"""
        pass

    # TODO 查询命令更改
    @filter.command("market")
    async def ping(self, event: AstrMessageEvent, name: str=""):
        """通过名称模糊查询跳蚤价格"""
        if(not name):
            yield event.plain_result("请提供物品名称");
            return

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
