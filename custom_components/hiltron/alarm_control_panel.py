from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    AlarmControlPanelEntityFeature,
    AlarmControlPanelState,
)
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([HiltronAlarmPanel(coordinator, entry)])

class HiltronAlarmPanel(AlarmControlPanelEntity):
    def __init__(self, coordinator, entry):
        self.coordinator = coordinator
        self._attr_unique_id = f"hiltron_alarm_panel_{entry.entry_id}"
        self._attr_name = "Centrale"
        self._attr_supported_features = (
            AlarmControlPanelEntityFeature.ARM_AWAY
            | AlarmControlPanelEntityFeature.ARM_HOME
            | AlarmControlPanelEntityFeature.ARM_NIGHT
        )
        self._attr_code_arm_required = False
        self._attr_code_disarm_required = False
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Hiltron Protec8 GSM",
            "manufacturer": "Hiltron",
            "model": "Protec8 GSM (Smart Bridge)",
            "sw_version": "2.0-Native",
        }

    @property
    def should_poll(self):
        return False

    @property
    def available(self):
        return self.coordinator.last_update_success

    @property
    def state(self):
        data = self.coordinator.data
        if not data or len(data) <= 34:
            return None
        
        state_byte = f"{data[34]:02x}"
        if state_byte == '03':
            return AlarmControlPanelState.TRIGGERED
        elif (int(state_byte[0], 16) & 1) > 0:
            return AlarmControlPanelState.ARMING
        elif (int(state_byte[0], 16) & 2) > 0:
            return AlarmControlPanelState.PENDING
        
        STATUS_MAP = {
            '0': AlarmControlPanelState.DISARMED,
            '1': AlarmControlPanelState.ARMED_AWAY,
            '5': AlarmControlPanelState.ARMED_HOME,
            'd': AlarmControlPanelState.ARMED_NIGHT,
        }
        return STATUS_MAP.get(state_byte[1], None)

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))

    async def async_alarm_disarm(self, code=None):
        await self.coordinator.async_send_key("00")
        await self.coordinator.async_request_refresh()

    async def async_alarm_arm_away(self, code=None):
        await self.coordinator.async_send_key("01")
        await self.coordinator.async_request_refresh()

    async def async_alarm_arm_home(self, code=None):
        await self.coordinator.async_send_key("02")
        await self.coordinator.async_request_refresh()

    async def async_alarm_arm_night(self, code=None):
        await self.coordinator.async_send_key("03")
        await self.coordinator.async_request_refresh()