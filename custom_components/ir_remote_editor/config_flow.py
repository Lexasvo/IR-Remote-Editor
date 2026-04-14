"""Config flow for IR Remote Editor."""
from __future__ import annotations

import logging
import re
from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Доступные частоты (кГц)
FREQUENCIES = ["36", "38", "40", "56"]


class IRRemoteConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for IR Remote Editor."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            for entry in self._async_current_entries():
                if entry.data.get("remote_name") == user_input["remote_name"]:
                    errors["base"] = "already_configured"
                    break
            if not errors:
                return self.async_create_entry(
                    title=user_input["remote_name"],
                    data={
                        "remote_name": user_input["remote_name"],
                        "esphome_device": user_input.get("esphome_device", "yandex_ir"),
                        "buttons": []
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("remote_name"): str,
                vol.Optional("esphome_device", default="yandex_ir"): str,
            }),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return IRRemoteOptionsFlow(config_entry)


class IRRemoteOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for IR Remote Editor."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._entry = config_entry
        self._buttons = config_entry.data.get("buttons", []).copy()
        self._selected_index = None
        self._action = None

    def _sanitize_name(self, name: str) -> str:
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

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            action = user_input.get("action")
            if action == "add":
                return await self.async_step_add_button()
            elif action == "edit":
                self._action = "edit"
                return await self.async_step_select_button()
            elif action == "delete":
                self._action = "delete"
                return await self.async_step_select_button()
            elif action == "view":
                self._action = "view"
                return await self.async_step_select_button()
            elif action == "config":
                return await self.async_step_configure_device()

        menu_options = {"add": "➕ Добавить кнопку", "config": "⚙️ Настройки устройства"}
        if self._buttons:
            menu_options["edit"] = "✏️ Редактировать кнопку"
            menu_options["delete"] = "❌ Удалить кнопку"
            menu_options["view"] = "👁️ Просмотреть RAW код"

        buttons_list = "\n".join([f"• {b['name']} ({b.get('frequency', '38')} kHz)" for b in self._buttons]) if self._buttons else "❌ Нет кнопок"

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({vol.Required("action"): vol.In(menu_options)}),
            description_placeholders={"current_buttons": buttons_list}
        )

    async def async_step_add_button(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Add a new button."""
        if user_input is not None:
            self._buttons.append({
                "name": user_input["name"],
                "code": user_input["code"],
                "icon": user_input.get("icon", "mdi:remote"),
                "frequency": user_input.get("frequency", "38"),
            })
            await self._save_buttons()
            return await self.async_step_init()

        return self.async_show_form(
            step_id="add_button",
            data_schema=vol.Schema({
                vol.Required("name"): str,
                vol.Required("code"): str,
                vol.Optional("icon", default="mdi:remote"): selector.IconSelector(),
                vol.Optional("frequency", default="38"): vol.In(FREQUENCIES),
            }),
        )

    async def async_step_select_button(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Select a button to edit/delete/view."""
        if not self._buttons:
            return self.async_abort(reason="no_buttons")

        if user_input is not None:
            self._selected_index = int(user_input["button_index"])
            if self._action == "edit":
                return await self.async_step_edit_button()
            elif self._action == "delete":
                return await self.async_step_confirm_delete()
            elif self._action == "view":
                return await self.async_step_view_button(None)

        button_options = {str(i): f"{b['name']} ({b.get('frequency', '38')} kHz)" for i, b in enumerate(self._buttons)}
        
        titles = {
            "edit": "Выберите кнопку для редактирования",
            "delete": "Выберите кнопку для удаления",
            "view": "Выберите кнопку для просмотра RAW кода"
        }
        title = titles.get(self._action, "Выберите кнопку")

        return self.async_show_form(
            step_id="select_button",
            data_schema=vol.Schema({vol.Required("button_index"): vol.In(button_options)}),
            description_placeholders={"title": title}
        )

    async def async_step_edit_button(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Edit an existing button."""
        current = self._buttons[self._selected_index]
        old_name = current["name"]
        
        if user_input is not None:
            new_name = user_input["name"]
            
            self._buttons[self._selected_index] = {
                "name": new_name,
                "code": current["code"],
                "icon": user_input.get("icon", current.get("icon", "mdi:remote")),
                "frequency": user_input.get("frequency", current.get("frequency", "38")),
            }
            await self._save_buttons()
            
            if old_name != new_name:
                await self._remove_entity(old_name)
            
            return await self.async_step_init()
        
        return self.async_show_form(
            step_id="edit_button",
            data_schema=vol.Schema({
                vol.Required("name", default=current["name"]): str,
                vol.Optional("icon", default=current.get("icon", "mdi:remote")): selector.IconSelector(),
                vol.Optional("frequency", default=current.get("frequency", "38")): vol.In(FREQUENCIES),
            }),
            description_placeholders={
                "button_name": current["name"],
                "raw_code": current["code"][:200] + "..." if len(current["code"]) > 200 else current["code"]
            }
        )

    async def async_step_view_button(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """View RAW code of selected button."""
        current = self._buttons[self._selected_index]
        
        if user_input is not None:
            return await self.async_step_init()
        
        return self.async_show_form(
            step_id="view_button",
            data_schema=vol.Schema({}),
            description_placeholders={
                "button_name": current["name"],
                "frequency": current.get("frequency", "38"),
                "raw_code": current["code"]
            }
        )

    async def async_step_confirm_delete(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Confirm button deletion."""
        button = self._buttons[self._selected_index]
        
        if user_input is not None:
            if user_input.get("confirm"):
                button_name = button["name"]
                del self._buttons[self._selected_index]
                await self._save_buttons()
                await self._remove_entity(button_name)
                _LOGGER.warning("🗑️ Deleted button: %s", button_name)
            
            return await self.async_step_init()

        raw_code = button["code"]
        if len(raw_code) > 100:
            raw_code = raw_code[:100] + "..."

        return self.async_show_form(
            step_id="confirm_delete",
            data_schema=vol.Schema({
                vol.Required("confirm", default=False): bool,
            }),
            description_placeholders={
                "button_name": button["name"],
                "frequency": button.get("frequency", "38"),
                "button_code": raw_code
            }
        )

    async def async_step_configure_device(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Configure ESPHome device."""
        if user_input is not None:
            new_data = dict(self._entry.data)
            new_data["remote_name"] = user_input["remote_name"]
            new_data["esphome_device"] = user_input["esphome_device"]
            self.hass.config_entries.async_update_entry(self._entry, data=new_data, title=user_input["remote_name"])
            await self.hass.config_entries.async_reload(self._entry.entry_id)
            return await self.async_step_init()

        return self.async_show_form(
            step_id="configure_device",
            data_schema=vol.Schema({
                vol.Required("remote_name", default=self._entry.data.get("remote_name", "")): str,
                vol.Optional("esphome_device", default=self._entry.data.get("esphome_device", "")): str,
            }),
        )

    async def _save_buttons(self) -> None:
        """Save buttons to config entry."""
        new_data = dict(self._entry.data)
        new_data["buttons"] = self._buttons
        self.hass.config_entries.async_update_entry(self._entry, data=new_data)
        await self.hass.config_entries.async_reload(self._entry.entry_id)

    async def _remove_entity(self, button_name: str) -> None:
        """Remove entity from registry."""
        entity_registry = er.async_get(self.hass)
        safe_name = self._sanitize_name(button_name)
        entity_id = f"button.{safe_name}"
        
        if entity_registry.async_get(entity_id):
            entity_registry.async_remove(entity_id)
            _LOGGER.warning("🧹 Removed entity: %s", entity_id)
