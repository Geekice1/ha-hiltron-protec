from homeassistant.components.switch import SwitchEntity
from .const import DOMAIN

BYPASS_EXCLUDE = {
    '1': '06', '2': '07', '3': '08', '4': '09',
    '5': '0a', '6': '0b', '7': '0c', '8': '0d', '24h': '0f'
}

BYPASS_INCLUDE = {
    '1': '10', '2': '11', '3': '12', '4': '13',
    '5': '14', '6': '15', '7': '16', '8': '17', '24h': '19'
}

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for z in list(range(1, 9)) + ["24h"]:
        entities.append(HiltronBypassSwitch(coordinator, entry, str(z)))
    async_add_entities(entities)

class HiltronBypassSwitch(SwitchEntity):
    def __init__(self, coordinator, entry, zone_str):
        self.coordinator = coordinator
        self.zone_str = zone_str
        label = f"Escludi Zona {zone_str}" if zone_str != "24h" else "Escludi Zona 24H"
        icon = "mdi:shield-off-outline" if zone_str != "24h" else "mdi:alert-octagon"
        
        self._attr_unique_id = f"hiltron_switch_bypass_{zone_str}_{entry.entry_id}"
        self._attr_name = label
        self._attr_icon = icon
        self._attr_device_info = {"identifiers": {(DOMAIN, entry.entry_id)}}

    @property
    def should_poll(self): return False
    @property
    def available(self): return self.coordinator.last_update_success

    @property
    def is_on(self):
        data = self.coordinator.data
        if not data:
            return False
        if self.zone_str != "24h":
            if len(data) <= 36: return False
            z = int(self.zone_str)
            return (data[36] & (1 << (z - 1))) > 0
        else:
            if len(data) <= 38: return False
            return (data[38] & 1) > 0

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))

    async def async_turn_on(self, **kwargs):
        key = BYPASS_EXCLUDE.get(self.zone_str)
        if key:
            await self.coordinator.async_send_key(key)
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        key = BYPASS_INCLUDE.get(self.zone_str)
        if key:
            await self.coordinator.async_send_key(key)
            await self.coordinator.async_request_refresh()