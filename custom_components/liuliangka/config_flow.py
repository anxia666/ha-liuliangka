"""流量卡配置流"""
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN, CONF_ICCID, CONF_CUSTOM_ID, CONF_TOKEN


DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ICCID): str,
        vol.Optional(CONF_CUSTOM_ID, default="7505121"): str,
        vol.Required(CONF_TOKEN): str,
    }
)


class TrafficCardConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """流量卡配置流"""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(
                title="流量卡", data=user_input
            )
        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return TrafficCardOptionsFlow()


class TrafficCardOptionsFlow(config_entries.OptionsFlow):
    """在集成卡片「配置」里更新 token（无需删除重添）"""

    async def async_step_init(self, user_input=None):
        errors = {}
        cur = self.config_entry.data or {}

        if user_input is not None:
            token = (user_input.get(CONF_TOKEN) or "").strip()
            if not token:
                errors["base"] = "token_required"
            else:
                new_data = {
                    CONF_ICCID: (user_input.get(CONF_ICCID) or cur.get(CONF_ICCID) or "").strip(),
                    CONF_CUSTOM_ID: (user_input.get(CONF_CUSTOM_ID) or cur.get(CONF_CUSTOM_ID) or "7505121").strip(),
                    CONF_TOKEN: token,
                }
                self.hass.config_entries.async_update_entry(
                    self.config_entry, data=new_data
                )
                # 数据已更新；__init__ 注册的 update_listener 会自动 reload 使新 token 生效
                return self.async_create_entry(title="", data={})

        schema = vol.Schema(
            {
                vol.Required(CONF_ICCID, default=cur.get(CONF_ICCID, "")): str,
                vol.Optional(CONF_CUSTOM_ID, default=cur.get(CONF_CUSTOM_ID, "7505121")): str,
                vol.Required(CONF_TOKEN, default=cur.get(CONF_TOKEN, "")): str,
            }
        )
        return self.async_show_form(
            step_id="init", data_schema=schema, errors=errors
        )
