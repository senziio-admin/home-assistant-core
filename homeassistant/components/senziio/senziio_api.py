"""API for interacting with Senziio Devices."""

import asyncio
import json
import logging
from typing import Optional

from homeassistant.components.mqtt import async_publish, async_subscribe
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .exceptions import MQTTNotEnabled

_LOGGER = logging.getLogger(__name__)


class Senziio:
    """Handle commands for Senziio sensor."""

    TIMEOUT = 10

    def __init__(self, hass: HomeAssistant, device_id: str, device_model: str) -> None:
        """Initialize instance."""
        self.hass = hass
        self.model_key = "-".join(device_model.lower().split())
        self.topics = {
            "info_req": f"cmd/{self.model_key}/{device_id}/device-info/req",
            "info_res": f"cmd/{self.model_key}/{device_id}/device-info/res",
        }

    async def get_info(self) -> Optional[dict]:
        """Get device info through mqtt.

        Example:
            {
              "model": "Theia Pro",
              "fw-version": "1.0.0",
              "hw-version": "1.0.0",
              "serial-number": "theia-pro-2F3X56E2ABCD",
              "mac-wifi": "2F:3D:56:E2:0A:BB",
              "mac-ethernet": "2F:3D:56:E2:0A:FF",
            }

        """
        device_info = {}
        response = asyncio.Event()

        async def handle_response(message):
            """Handle device info response."""
            nonlocal device_info
            try:
                device_info = json.loads(message.payload)
            except json.JSONDecodeError:
                _LOGGER.error(
                    "Could not parse device info payload: %s", message.payload
                )
            response.set()

        try:
            unsubscribe_callback = await async_subscribe(
                self.hass,
                self.topics["info_res"],
                handle_response,
            )

            await async_publish(
                self.hass,
                self.topics["info_req"],
                "Device info request",
                qos=1,
                retain=False,
            )
        except HomeAssistantError as error:
            _LOGGER.error("Could not set MQTT topics")
            raise MQTTNotEnabled from error

        try:
            await asyncio.wait_for(response.wait(), self.TIMEOUT)
            return device_info
        except TimeoutError:
            return None
        finally:
            unsubscribe_callback()
