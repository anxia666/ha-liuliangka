"""流量卡常量"""
DOMAIN = "liuliangka"
CONF_ICCID = "iccid"
CONF_CUSTOM_ID = "custom_id"
CONF_TOKEN = "token"
SCAN_INTERVAL_SECONDS = 600
API_URL = "http://yw.jinmaiiot.com/side/user/phoneCard/cardInfo"
ORIGIN = "http://xzf.nuantianxx.top"
RESOURCE_NAME = "小末智能"
SENSOR_TYPES = {
    "usedgb": {"name": "已用流量", "unit": "GB", "icon": "mdi:download", "state_class": "measurement"},
    "remaingb": {"name": "剩余流量", "unit": "GB", "icon": "mdi:upload", "state_class": "measurement"},
    "totalgb": {"name": "总流量", "unit": "GB", "icon": "mdi:server", "state_class": "measurement"},
    "balance": {"name": "账户余额", "unit": "元", "icon": "mdi:cash", "state_class": "measurement"},
    "giftbalance": {"name": "赠送余额", "unit": "元", "icon": "mdi:gift", "state_class": "measurement"},
    "cardstatustext": {"name": "卡片状态", "unit": None, "icon": "mdi:sim"},
    "expiretime": {"name": "到期时间", "unit": None, "icon": "mdi:calendar"},
    "updatetime": {"name": "更新时间", "unit": None, "icon": "mdi:update"},
}
