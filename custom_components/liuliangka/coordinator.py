"""流量卡协调器"""
import logging
import time
import gzip
import json
import urllib.parse
import urllib.request
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN, CONF_ICCID, CONF_CUSTOM_ID, CONF_TOKEN,
    SCAN_INTERVAL_SECONDS, API_URL, ORIGIN, RESOURCE_NAME,
)

_LOGGER = logging.getLogger(__name__)

FIELD_MAP = {
    "usedgb": ("nowUsedFlowVirtual", lambda v: round(float(v) / 1024, 2) if v else None),
    "remaingb": ("remain", lambda v: round(v / 1024, 2)),
    "totalgb": ("virtualEnable", lambda v: round(float(v) / 1024, 2) if v else None),
    "balance": ("balance", float),
    "giftbalance": ("giveBalanceMoney", float),
    "cardstatustext": ("cardStatus", lambda v: "正常" if v == 2002 else "异常"),
    "expiretime": ("expireTime", str),
    "updatetime": ("updateTime", str),
}


class TrafficCardCoordinator(DataUpdateCoordinator):
    """流量卡协调器"""

    def __init__(self, hass, config):
        super().__init__(
            hass, _LOGGER, name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL_SECONDS),
        )
        self._iccid = config[CONF_ICCID]
        self._custom_id = config.get(CONF_CUSTOM_ID, "7505121")
        self._token = config[CONF_TOKEN]

    async def _async_update_data(self):
        """拉取数据"""
        try:
            data = await self.hass.async_add_executor_job(self._fetch)
        except Exception as err:
            raise UpdateFailed(f"金迈 API 请求失败: {err}") from err
        return self._parse(data)

    def _fetch(self):
        """同步拉取金迈数据"""
        params = {
            "iccid": self._iccid,
            "timestamp": str(int(time.time())),
            "customId": self._custom_id,
            "source": "wxPublic",
            "registerResource": "2",
            "resourceName": RESOURCE_NAME,
        }
        url = f"{API_URL}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, method="GET")
        req.add_header("token", self._token)
        req.add_header("customId", self._custom_id)
        req.add_header("Accept", "*/*")
        req.add_header("Accept-Language", "zh-CN,zh-Hans;q=0.9")
        req.add_header("Accept-Encoding", "gzip, deflate")
        req.add_header("Origin", ORIGIN)
        req.add_header("Referer", ORIGIN + "/")
        req.add_header("Content-Type", "application/json")
        req.add_header("User-Agent", "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15")

        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read()
            if resp.headers.get("Content-Encoding") == "gzip" or raw[:2] == b"\x1f\x8b":
                raw = gzip.decompress(raw)
            result = json.loads(raw.decode("utf-8"))

        if result.get("code") != 200:
            raise UpdateFailed(f"API 错误 {result.get('code')}: {result.get('msg')}")
        d = result.get("data", {})
        d["remain"] = float(d.get("virtualEnable", 0)) - float(d.get("nowUsedFlowVirtual", 0))
        return d

    def _parse(self, d):
        """解析数据"""
        parsed = {}
        for key, (field, converter) in FIELD_MAP.items():
            try:
                parsed[key] = converter(d.get(field))
            except (TypeError, ValueError):
                parsed[key] = None
        return parsed