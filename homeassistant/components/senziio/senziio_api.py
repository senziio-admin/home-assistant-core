"""API for interacting with Senziio Devices."""

from abc import ABC
import asyncio
from collections.abc import Callable
import json
import logging

from homeassistant.components.mqtt import async_publish, async_subscribe
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .exceptions import MQTTNotEnabled

_LOGGER = logging.getLogger(__name__)


class SenziioMQTT(ABC):
    """Senziio MQTT communication interface."""

    async def publish(self, topic, payload):
        """Publish to topic with a payload."""

    async def subscribe(self, topic, callback):
        """Subscribe to topic with a callback."""


class Senziio:
    """Senziio device communications."""

    TIMEOUT = 10

    def __init__(self, device_id: str, device_model: str, mqtt: SenziioMQTT) -> None:
        """Initialize instance."""
        self.device_id = device_id
        self.model_key = "-".join(device_model.lower().split())
        self.mqtt = mqtt
        self.topics = {
            "info_req": f"cmd/{self.model_key}/{device_id}/device-info/req",
            "info_res": f"cmd/{self.model_key}/{device_id}/device-info/res",
            "data": f"dt/{self.model_key}/{device_id}",
        }

    @property
    def id(self):
        """Return ID of device."""
        return self.device_id

    async def get_info(self):
        """Get device info."""
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

        unsubscribe_callback = await self.mqtt.subscribe(
            self.topics["info_res"],
            handle_response,
        )

        await self.mqtt.publish(
            self.topics["info_req"],
            "Device info request",
        )

        try:
            await asyncio.wait_for(response.wait(), self.TIMEOUT)
            return device_info
        except TimeoutError:
            return None
        finally:
            unsubscribe_callback()

    def entity_topic(self, entity: str) -> str:
        """Get topic for listening to entity data updates."""
        return f"{self.topics['data']}/{entity}"


class SenziioCommunicationError(Exception):
    """Error when can not communicate with a Senziio device."""


class SenziioHAMQTT(SenziioMQTT):  # keep only this class in HA (where?)
    """Senziio MQTT interface using MQTT integration."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize MQTT interface for Senziio devices."""
        self._hass = hass

    async def publish(self, topic: str, payload: str) -> None:
        """Publish to topic with a payload."""
        try:
            return await async_publish(self._hass, topic, payload)
        except HomeAssistantError as error:
            _LOGGER.error("Could not publish to MQTT topic")
            raise MQTTNotEnabled from error

    async def subscribe(self, topic: str, callback: Callable) -> Callable:
        """Subscribe to topic with a callback."""
        try:
            return await async_subscribe(self._hass, topic, callback)
        except HomeAssistantError as error:
            _LOGGER.error("Could not subscribe to MQTT topic")
            raise MQTTNotEnabled from error
