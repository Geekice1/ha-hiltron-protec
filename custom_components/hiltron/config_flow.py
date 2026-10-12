import base64
import voluptuous as vol
import aiohttp
from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_MAC, CONF_PASSWORD, CONF_USER_CODE

class HiltronConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            ip = user_input["hiltron_ip"].strip()
            mac = user_input[CONF_MAC].strip()
            password = user_input[CONF_PASSWORD].strip()
            user_code = user_input[CONF_USER_CODE].strip()

            # Generazione stringa Base64 senza il più in mezzo
            raw_string = f"{mac}:{password}{user_code}"
            auth_bytes = raw_string.encode("utf-8")
            auth_token = base64.b64encode(auth_bytes).decode("utf-8")

            # --- VERIFICA CONNESSIONE E CREDENZIALI ---
            url = f"http://{ip}/user/data.cgi"
            headers = {"Authorization": f"Basic {auth_token}"}
            session = async_get_clientsession(self.hass)

            try:
                async with session.get(url, headers=headers, timeout=5) as response:
                    if response.status == 401:
                        errors["base"] = "invalid_auth"
                    elif response.status != 200:
                        errors["base"] = "cannot_connect"
                    else:
                        data = await response.read()
                        if not data or len(data) <= 40:
                            errors["base"] = "invalid_data"
                        else:
                            # Se tutto è ok, salviamo i dati
                            user_input["auth_token"] = auth_token
                            await self.async_set_unique_id(mac)
                            self._abort_if_unique_id_configured()

                            return self.async_create_entry(
                                title=f"Hiltron Protec8 ({mac})",
                                data=user_input
                            )
            except Exception:
                errors["base"] = "cannot_connect"

        # Schema ordinato con i campi richiesti e i selettori per mascherare i testi sensibili
        schema = vol.Schema({
            vol.Required("hiltron_ip", description={"suggested_value": "192.168.1."}): cv.string,
            vol.Required(CONF_MAC, description={"suggested_value": ""}): cv.string,
            vol.Required(CONF_PASSWORD): str,
            vol.Required(CONF_USER_CODE): str,
        })

        # Mappatura dei selettori UI per mascherare password e codice utente e dare etichette pulite
        data_schema = self.add_suggested_values_to_schema(
            vol.Schema({
                vol.Required("hiltron_ip"): str,
                vol.Required(CONF_MAC): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Required(CONF_USER_CODE): str,
            }),
            user_input or {}
        )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("hiltron_ip"): cv.string,
                vol.Required(CONF_MAC): cv.string,
                vol.Required(CONF_PASSWORD): selector_text_password(), # Mascherato
                vol.Required(CONF_USER_CODE): selector_text_password(), # Mascherato
            }),
            errors=errors
        )

from homeassistant.helpers.selector import selector

def selector_text_password():
    return selector({"text": {"type": "password"}})