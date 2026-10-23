"""流量卡传感器"""
from homeassistant.components.sensor import SensorEntity

from .const import DOMAIN, SENSOR_TYPES
from .coordinator import TrafficCardCoordinator


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator: TrafficCardCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        TrafficCardSensor(coordinator, key, conf, entry)
        for key, conf in SENSOR_TYPES.items()
    )


class TrafficCardSensor(SensorEntity):
    def __init__(self, coordinator, key, conf, entry):
        self.coordinator = coordinator
        self._key = key
        self._attr_name = conf["name"]
        self._attr_icon = conf["icon"]
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_should_poll = False
        if conf.get("unit"):
            self._attr_native_unit_of_measurement = conf["unit"]
        if conf.get("device_class"):
            self._attr_device_class = conf["device_class"]
        if conf.get("state_class"):
            self._attr_state_class = conf["state_class"]
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "随身WiFi",
            "manufacturer": "金迈物联",
        }

    @property
    def available(self):
        return self.coordinator.last_update_success

    @property
    def native_value(self):
        return self.coordinator.data.get(self._key)

    async def async_added_to_hass(self):
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )