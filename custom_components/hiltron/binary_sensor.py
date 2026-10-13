from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN

CLASSES = {
    1: BinarySensorDeviceClass.DOOR,
    2: BinarySensorDeviceClass.MOTION,
    3: BinarySensorDeviceClass.MOTION,
    4: BinarySensorDeviceClass.DOOR,
    5: BinarySensorDeviceClass.DOOR,
    6: BinarySensorDeviceClass.MOTION,
    7: BinarySensorDeviceClass.WINDOW,
    8: BinarySensorDeviceClass.MOTION,
}

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []

    # Zone da 1 a 8
    for z in range(1, 9):
        entities.append(HiltronZoneSensor(coordinator, entry, z))
    
    # Zona 24H (Tamper)
    entities.append(Hiltron24HSensor(coordinator, entry))
    
    # Sensore testuale Memoria Allarme
    entities.append(HiltronMemorySensor(coordinator, entry))

    async_add_entities(entities)

class HiltronZoneSensor(BinarySensorEntity):
    def __init__(self, coordinator, entry, zone_num):
        self.coordinator = coordinator
        self.zone_num = zone_num
        self._attr_unique_id = f"hiltron_binary_zone_{zone_num}_{entry.entry_id}"
        self._attr_name = f"Zona {zone_num}"
        self._attr_device_class = CLASSES.get(zone_num, BinarySensorDeviceClass.MOTION)
        self._attr_device_info = {"identifiers": {(DOMAIN, entry.entry_id)}}

    @property
    def should_poll(self): return False
    @property
    def available(self): return self.coordinator.last_update_success

    @property
    def is_on(self):
        data = self.coordinator.data
        if not data or len(data) <= 39:
            return False
        z_byte = data[39]
        return (z_byte & (1 << (self.zone_num - 1))) > 0

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))

class Hiltron24HSensor(BinarySensorEntity):
    def __init__(self, coordinator, entry):
        self.coordinator = coordinator
        self._attr_unique_id = f"hiltron_binary_zone_24h_{entry.entry_id}"
        self._attr_name = "Zona 24H (Tamper)"
        self._attr_device_class = BinarySensorDeviceClass.TAMPER
        self._attr_device_info = {"identifiers": {(DOMAIN, entry.entry_id)}}

    @property
    def should_poll(self): return False
    @property
    def available(self): return self.coordinator.last_update_success

    @property
    def is_on(self):
        data = self.coordinator.data
        if not data or len(data) <= 40:
            return False
        return (data[40] & 1) > 0

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))

class HiltronMemorySensor(BinarySensorEntity):
    def __init__(self, coordinator, entry):
        self.coordinator = coordinator
        self._attr_unique_id = f"hiltron_memory_{entry.entry_id}"
        self._attr_name = "Memoria Allarme"
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM
        self._attr_device_info = {"identifiers": {(DOMAIN, entry.entry_id)}}

    @property
    def should_poll(self): return False
    @property
    def available(self): return self.coordinator.last_update_success

    @property
    def _active_memories(self):
        data = self.coordinator.data
        if not data or len(data) <= 37:
            return []
        mem_1_8 = data[35]
        mem_24h = data[37]
        active = [f"Zona {z}" for z in range(1, 9) if (mem_1_8 & (1 << (z - 1))) > 0]
        if (mem_24h & 1) > 0:
            active.append("Zona 24H")
        return active

    @property
    def is_on(self):
        # False (spento/grigio) se lista vuota, True (giallo/rosso) se c'è memoria
        return len(self._active_memories) > 0

    @property
    def extra_state_attributes(self):
        mems = self._active_memories
        return {
            "zones": mems,
            "description": ", ".join(mems) if mems else "Nessuna"
        }

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))