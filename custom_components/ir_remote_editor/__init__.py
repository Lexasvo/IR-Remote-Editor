"""IR Remote Editor integration."""
from __future__ import annotations

import json
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.components.mqtt import async_subscribe

from .const import DOMAIN, MQTT_TOPIC_RESULT

_LOGGER = logging.getLogger(__name__)
PLATFORMS: list[Platform] = [Platform.BUTTON]

LEARNING_REMOTES = {}
PROCESSED_CODES = {}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up IR Remote Editor from a config entry."""
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    device_id = entry.data.get("esphome_device", "")
    if not device_id:
        device_id = "yandex_ir"
    
    topic = MQTT_TOPIC_RESULT.format(device=device_id)
    
    _LOGGER.error("=" * 60)
    _LOGGER.error("🔧 REGISTERING MQTT LISTENER")
    _LOGGER.error("   Entry ID: %s", entry.entry_id)
    _LOGGER.error("   Device: %s", device_id)
    _LOGGER.error("   Topic: %s", topic)
    _LOGGER.error("=" * 60)
    
    @callback
    async def mqtt_message_received(msg):
        """Handle MQTT message from Tasmota."""
        try:
            payload = json.loads(msg.payload)
        except json.JSONDecodeError:
            return
        
        if "IrReceived" not in payload:
            return
        
        ir_data = payload["IrReceived"]
        
        # Сохраняем ИСХОДНЫЙ RawData как есть (с буквами и знаками)!
        raw_str = ir_data.get("RawData", "")
        if not raw_str:
            return
        
        raw_code = "RAW: " + raw_str
        protocol = ir_data.get("Protocol", "RAW")
        bits = ir_data.get("Bits", "?")
        data_hex = ir_data.get("Data", "")
        
        _LOGGER.error("=" * 60)
        _LOGGER.error("📸 IR Signal Captured!")
        _LOGGER.error("   Protocol: %s", protocol)
        _LOGGER.error("   Bits: %s", bits)
        _LOGGER.error("   Data: %s", data_hex if data_hex else "(none)")
        _LOGGER.error("   RawData length: %d", len(raw_str))
        _LOGGER.error("=" * 60)
        
        code_id = raw_str[:100]
        
        if code_id == PROCESSED_CODES.get(entry.entry_id):
            _LOGGER.warning("⏭️ Already processed")
            return
        
        if entry.entry_id not in LEARNING_REMOTES:
            _LOGGER.warning("⚠️ Entry not in LEARNING_REMOTES")
            return
        
        if not LEARNING_REMOTES[entry.entry_id]:
            _LOGGER.warning("⚠️ Learning mode not active")
            return
        
        _LOGGER.error("🎓 CREATING BUTTON!")
        PROCESSED_CODES[entry.entry_id] = code_id
        
        hass.async_create_task(_auto_create_button(hass, entry, raw_code))
        LEARNING_REMOTES[entry.entry_id] = False
    
    unsubscribe = await async_subscribe(hass, topic, mqtt_message_received)
    entry.async_on_unload(unsubscribe)
    
    _LOGGER.error("✅ MQTT Listener registered for %s", topic)
    
    return True


async def _auto_create_button(hass: HomeAssistant, entry: ConfigEntry, code: str) -> None:
    """Auto-create a button."""
    _LOGGER.error("🔨 Creating button...")
    
    buttons = entry.data.get("buttons", []).copy()
    code_start = code[:50]
    
    for btn in buttons:
        if btn.get("code", "").startswith(code_start):
            _LOGGER.warning("⚠️ Button already exists")
            return
    
    auto_buttons = [b for b in buttons if b.get("name", "").startswith("Button ")]
    button_name = f"Button {len(auto_buttons) + 1}"
    
    buttons.append({
        "name": button_name,
        "code": code,
        "icon": "mdi:remote",
    })
    
    new_data = dict(entry.data)
    new_data["buttons"] = buttons
    hass.config_entries.async_update_entry(entry, data=new_data)
    
    await hass.config_entries.async_reload(entry.entry_id)
    _LOGGER.error("✅ Button created: %s", button_name)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if entry.entry_id in LEARNING_REMOTES:
        del LEARNING_REMOTES[entry.entry_id]
    if entry.entry_id in PROCESSED_CODES:
        del PROCESSED_CODES[entry.entry_id]
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


def set_learning_mode(entry_id: str, enabled: bool) -> None:
    LEARNING_REMOTES[entry_id] = enabled
    if enabled and entry_id in PROCESSED_CODES:
        del PROCESSED_CODES[entry_id]
    _LOGGER.error("🎓 set_learning_mode: %s = %s", entry_id, enabled)
