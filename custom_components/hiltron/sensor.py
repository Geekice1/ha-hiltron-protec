from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([HiltronMemorySensor(coordinator, entry)])

class HiltronMemorySensor(SensorEntity):
    def __init__(self, coordinator, entry):
        self.coordinator = coordinator
        self._attr_unique_id = f"hiltron_memory_text_{entry.entry_id}"
        self._attr_name = "Memoria Allarme"
        self._attr_device_info = {"identifiers": {(DOMAIN, entry.entry_id)}}

    @property
    def should_poll(self): 
        return False

    @property
    def available(self): 
        return self.coordinator.last_update_success

    @property
    def native_value(self):
        data = self.coordinator.data
        if not data or len(data) <= 37:
            return "Nessuna"
        mem_1_8 = data[35]
        mem_24h = data[37]
        active_mem = [f"Zona {z}" for z in range(1, 9) if (mem_1_8 & (1 << (z - 1))) > 0]
        if (mem_24h & 1) > 0:
            active_mem.append("Zona 24H")
        return ", ".join(active_mem) if active_mem else "Nessuna"

    @property
    def icon(self):
        if self.native_value == "Nessuna":
            return "mdi:history"
        return "mdi:alert-circle"

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))