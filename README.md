# IR Remote Editor for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/Lexasvo/ir-remote-editor.svg)](https://github.com/Lexasvo/ir-remote-editor/releases)

Integration for creating virtual IR remotes in Home Assistant. Works with ESP8266/ESP32 flashed with Tasmota firmware with IR support.

## ✨ Features

- 🎓 **Learning mode** — one press on a physical remote creates a button
- 🔘 **Auto button creation** — RAW code is saved automatically
- 📡 **Full RAW support** — any remotes, any protocols
- ⚙️ **UI configuration** — no need to edit YAML
- 🎚️ **Frequency selection** — 36/38/40/56 kHz for each button
- 🛡️ **Duplicate protection** — signal is sent exactly once
- 🧹 **Button management** — edit, delete, view RAW code

## 📦 Installation

### Via HACS (recommended)
[![Add to HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Lexasvo&repository=IR-Remote-Editor&category=Integration)

1. Add the custom repository: `https://github.com/Lexasvo/ir-remote-editor`
2. Install the "IR Remote Editor" integration
3. Restart Home Assistant

### Manual

Copy the `custom_components/ir_remote_editor` folder to `/config/custom_components/`

## 🔧 Requirements

- Home Assistant 2024.1+
- ESP8266/ESP32 with Tasmota firmware and IR support
- MQTT broker (Mosquitto)

## 📡 Tasmota Configuration

### 1. Firmware
Download and install the firmware with IR support:
- [tasmota-ir.bin](https://github.com/arendst/Tasmota/releases/download/v15.3.0/tasmota-ir.bin)

### 2. Pin configuration via web interface

1. Open the Tasmota web interface (`http://192.168.x.x`)
2. Go to **Configuration → Configure Module**
3. Select module type: **Generic (18)** (at the very bottom of the list)
4. Configure the pins:
   - **GPIO5** → `IRrecv (51)`
   - **GPIO14** → `IRsend (52)`
5. Click **Save**. The device will restart.

### 3. Enable RAW support via console
  SetOption58 1
  
## 4. MQTT Configuration
1) Host: MQTT broker host
2) Port: MQTT port
3) User: MQTT username
4) Password: MQTT password
5) Topic: `yandex_ir`

# 5. Known Issues:
1) After deleting a button via the GUI, they remain in inactive mode
2) After editing a button via the GUI, it gets duplicated; the old one becomes inactive


# IR Remote Editor для Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/Lexasvo/ir-remote-editor.svg)](https://github.com/Lexasvo/ir-remote-editor/releases)

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
[![Add to HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Lexasvo&repository=IR-Remote-Editor&category=Integration)

1. Добавьте пользовательский репозиторий: `https://github.com/Lexasvo/ir-remote-editor`
2. Установите интеграцию "IR Remote Editor"
3. Перезагрузите Home Assistant

### Вручную

Скопируйте папку `custom_components/ir_remote_editor` в `/config/custom_components/`

## 🔧 Требования

- Home Assistant 2024.1+
- ESP8266/ESP32 с прошивкой Tasmota с поддержкой IR
- MQTT брокер (Mosquitto)

## 📡 Настройка Tasmota

### 1. Прошивка
Скачайте и установите прошивку с поддержкой IR:
- [tasmota-ir.bin](https://github.com/arendst/Tasmota/releases/download/v15.3.0/tasmota-ir.bin)

### 2. Настройка пинов через веб-интерфейс

1. Откройте веб-интерфейс Tasmota (`http://192.168.x.x`)
2. Перейдите в **Configuration → Configure Module**
3. Выберите тип модуля: **Generic (18)** (в самом низу списка)
4. Настройте пины:
   - **GPIO5** → `IRrecv (51)`
   - **GPIO14** → `IRsend (52)`
5. Нажмите **Save**. Устройство перезагрузится.

### 3. Включить поддержку RAW через консоль
SetOption58 1

## 4. Настройка MQTT

1) Host: хост MQTT
2) Port: порт MQTT
3) User: логин MQTT
4) Password: пароль MQTT
5) Topic: yandex_ir

# 5. Известные проблемы: 
1) после удаления кнопки через GUI они остаются в неактивном режиме
2) после изменения кнопки через GUI она дублируется, старая станет неактивной.

