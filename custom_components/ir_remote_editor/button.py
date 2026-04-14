"""Button platform for IR Remote Editor."""
from __future__ import annotations

import logging
import re
import time
import asyncio
from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN, ICON_BUTTON_DEFAULT, MANUFACTURER, MODEL

_LOGGER = logging.getLogger(__name__)

LAST_SEND_TIME = 0
SEND_COOLDOWN = 0.5
SEND_LOCK = False


def sanitize_name(name: str) -> str:
    """Convert name to safe entity_id."""
    translit = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
        'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
        'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
        'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch',
        'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya',
    }
    safe = name
    for ru, en in translit.items():
        safe = safe.replace(ru, en)
    safe = re.sub(r'[^a-zA-Z0-9]', '_', safe.lower())
    safe = re.sub(r'_+', '_', safe)
    return safe.strip('_')


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up IR Remote buttons."""
    try:
        buttons = []
        device_id = config_entry.data.get("esphome_device", "yandex_ir")
        
        buttons.append(IRLearningModeButton(config_entry, device_id))
        buttons.append(IRClearCodeButton(config_entry, device_id))
        
        for button_data in config_entry.data.get("buttons", []):
            buttons.append(
                IRRemoteButton(
                    config_entry,
                    button_data["name"],
                    button_data["code"],
                    button_data.get("icon", ICON_BUTTON_DEFAULT),
                    device_id,
                    button_data.get("frequency", "38"),
                )
            )
        
        if buttons:
            async_add_entities(buttons)
            _LOGGER.warning("✅ Added %d buttons", len(buttons))
            
    except Exception as e:
        _LOGGER.error("Failed: %s", e, exc_info=True)


class IRRemoteButton(ButtonEntity):
    """IR Remote button."""

    def __init__(
        self,
        config_entry: ConfigEntry,
        name: str,
        ir_code: str,
        icon: str,
        device_id: str,
        frequency: str,
    ) -> None:
        """Initialize the button."""
        self._config_entry = config_entry
        self._attr_name = name
        self._attr_unique_id = f"{config_entry.entry_id}_{sanitize_name(name)}"
        self._ir_code = ir_code
        self._attr_icon = icon or ICON_BUTTON_DEFAULT
        self._device_id = device_id
        self._frequency = int(frequency)
        self._last_press = 0
        
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.entry_id)},
            name=config_entry.data["remote_name"],
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    async def async_press(self) -> None:
        """Send IR code via MQTT."""
        global LAST_SEND_TIME, SEND_LOCK
        
        if SEND_LOCK:
            _LOGGER.warning("⏭️ SEND LOCKED")
            return
        
        now = time.time()
        if now - LAST_SEND_TIME < SEND_COOLDOWN:
            _LOGGER.warning("⏭️ Debounced")
            return
        
        SEND_LOCK = True
        LAST_SEND_TIME = now
        
        try:
            code = self._ir_code.strip()
            if not code.startswith("RAW:"):
                _LOGGER.error("Not a RAW code")
                return
            
            # Получаем исходную строку RawData (с буквами и знаками)
            raw_str = code[4:].strip()
            
            if not raw_str:
                _LOGGER.error("Empty RAW data")
                return
            
            _LOGGER.info("📤 Sending RAW @ %d kHz", self._frequency)
            
            # Отправляем как есть: частота,исходный_RawData
            data_str = f"{self._frequency},{raw_str}"
            
            topic = f"cmnd/{self._device_id}/IRsend"
            
            await self.hass.services.async_call(
                "mqtt", "publish",
                {"topic": topic, "payload": data_str},
                blocking=False
            )
            
            _LOGGER.info("✅ Sent to MQTT: %s", topic)
            _LOGGER.debug("Payload: %s", data_str[:100])
            
            await asyncio.sleep(0.3)
        except Exception as e:
            _LOGGER.error("Failed: %s", e, exc_info=True)
        finally:
            SEND_LOCK = False


class IRLearningModeButton(ButtonEntity):
    """Button to activate learning mode."""

    def __init__(self, config_entry: ConfigEntry, device_id: str):
        self._config_entry = config_entry
        self._device_id = device_id
        self._attr_name = "🎓 Режим обучения"
        self._attr_unique_id = f"{config_entry.entry_id}_learning"
        self._attr_icon = "mdi:teach"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.entry_id)},
            name=config_entry.data["remote_name"],
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    async def async_press(self):
        from . import set_learning_mode
        set_learning_mode(self._config_entry.entry_id, True)
        _LOGGER.warning("🎓 Learning mode ON")


class IRClearCodeButton(ButtonEntity):
    """Button to turn off learning mode."""

    def __init__(self, config_entry: ConfigEntry, device_id: str):
        self._config_entry = config_entry
        self._device_id = device_id
        self._attr_name = "🧹 Выключить обучение"
        self._attr_unique_id = f"{config_entry.entry_id}_clear"
        self._attr_icon = "mdi:broom"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.entry_id)},
            name=config_entry.data["remote_name"],
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    async def async_press(self):
        from . import set_learning_mode
        set_learning_mode(self._config_entry.entry_id, False)
        _LOGGER.warning("🧹 Learning mode OFF")
