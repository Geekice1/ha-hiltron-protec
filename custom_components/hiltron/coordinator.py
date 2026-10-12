import logging
from datetime import timedelta
import async_timeout
import aiohttp

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)

class HiltronDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, ip, auth_token):
        self.ip = ip
        self.auth_token = auth_token
        self.url = f"http://{ip}/user/data.cgi"
        self.session = async_get_clientsession(hass)
        
        super().__init__(
            hass,
            _LOGGER,
            name="Hiltron Protec8",
            update_interval=timedelta(seconds=2),
        )

    async def _async_update_data(self):
        headers = {"Authorization": f"Basic {self.auth_token}"}
        try:
            async with async_timeout.timeout(3):
                async with self.session.get(self.url, headers=headers) as response:
                    if response.status != 200:
                        raise UpdateFailed(f"Errore HTTP dalla centrale: {response.status}")
                    data = await response.read()
                    if not data or len(data) <= 40:
                        raise UpdateFailed("Dati ricevuti dalla centrale incompleti o vuoti")
                    return data
        except Exception as err:
            raise UpdateFailed(f"Impossibile comunicare con la centrale Hiltron: {err}")

    async def async_send_key(self, key_param):
        """Invia un comando CGI (es. armamento o bypass) alla centrale"""
        headers = {"Authorization": f"Basic {self.auth_token}"}
        url = f"{self.url}?key={key_param}"
        try:
            async with async_timeout.timeout(3):
                async with self.session.get(url, headers=headers) as response:
                    return response.status == 200
        except Exception as err:
            _LOGGER.error("Errore nell'invio del comando key=%s: %s", key_param, err)
            return False