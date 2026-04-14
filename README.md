# IR Remote Editor для Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/Lexasvo/ir-remote-editor.svg)](https://github.com/Lexasvo/ir-remote-editor/releases)
[![GitHub License](https://img.shields.io/github/license/Lexasvo/ir-remote-editor.svg)](LICENSE)

Интеграция для создания виртуальных ИК-пультов в Home Assistant. Работает с ESP8266/ESP32, прошитыми Tasmota с поддержкой IR.

## ✨ Возможности

- 🎓 **Режим обучения** — одно нажатие на физический пульт создаёт кнопку
- 🔘 **Авто-создание кнопок** — RAW код сохраняется автоматически
- 📡 **Полная поддержка RAW** — любые пульты, любые протоколы
- ⚙️ **Настройка через UI** — не нужно править YAML
- 🎚️ **Выбор частоты** — 36/38/40/56 кГц для каждой кнопки
- 🛡️ **Защита от дублирования** — сигнал отправляется ровно один раз
- 🧹 **Управление кнопками** — редактирование, удаление, просмотр RAW кода

## 📦 Установка

### Через HACS (рекомендуется)
[![Add to HACS](https://camo.githubusercontent.com/49f849a6409cdcad49e32d41115ab078f810d960b35466436e028d4552aadd40/68747470733a2f2f6d792e686f6d652d617373697374616e742e696f2f6261646765732f686163735f7265706f7369746f72792e737667)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Lexasvo&repository=IR-Remote-Editor&category=Integration)

1. Добавьте пользовательский репозиторий: `https://github.com/Lexasvo/ir-remote-editor`
2. Установите интеграцию "IR Remote Editor"
3. Перезагрузите Home Assistant

### Вручную

Скопируйте папку `custom_components/ir_remote_editor` в `/config/custom_components/`

## 🔧 Требования

- Home Assistant 2024.1+
- ESP8266/ESP32 с прошивкой **Tasmota 14.x** с поддержкой IR
- MQTT брокер (Mosquitto)

## 📡 Настройка Tasmota

### 1. Прошивка
Скачайте и установите прошивку с поддержкой IR:
- [tasmota-ir.bin](http://ota.tasmota.com/tasmota/release-14.4.0/tasmota-ir.bin)

### 2. Настройка пинов через веб-интерфейс

1. Откройте веб-интерфейс Tasmota (`http://192.168.x.x`)
2. Перейдите в **Configuration → Configure Module**
3. Выберите тип модуля: **Generic (18)** (в самом низу списка)
4. Настройте пины:
   - **GPIO5** → `IRrecv (51)`
   - **GPIO14** → `IRsend (52)`
5. Нажмите **Save**. Устройство перезагрузится.

# Включить поддержку RAW через консоль
SetOption58 1

## 3. Настройка MQTT

1) Host: хост MQTT
2) Port: порт MQTT
3) User: логин MQTT
4) Password: пароль MQTT
5) Topic: yandex_ir
