# Sentinel - Sistema de Monitoreo Visual

**Rol**: Senior Automation Engineer & Expert in Computer Vision  
**Objetivo**: Desarrollar un sistema de monitoreo visual para Hubstaff, optimizado para detectar la transición de "Budget Agotado" (Rojo) a "Multiple limits / Disponible" (Gris).

---

## Stack Técnico

| Componente | Tecnología |
|------------|-------------|
| Lenguaje | Python 3.10+ |
| Visión | opencv-python |
| Control | pyautogui |
| Procesamiento | numpy |
| Config | python-dotenv |
| Alertas | winsound |
| Target OS | Windows (High-DPI) |

---

## Estructura de Archivos

```
SENTINELA/
├── .env              # Configuración (tokens, coordenadas)
├── config.py          # Módulo de carga de configuración
├── alerts.py         # AlertManager (Telegram, WhatsApp, beep)
├── calibrate.py      # Script de calibración interactivo
├── sentinel.pyw      # Monitor principal (sin consola)
├── templates/       # Templates de captura
│   └── budget_red.png
├── sentinel.log      # Log de ejecución
└── PLAN.md         # Este documento
```

---

## Módulos

### 1. config.py
- Carga de variables desde `.env`
- Creación automática de .env por defecto
- Retorna diccionario CONFIG con todos los parámetros

### 2. alerts.py - AlertManager
```python
class AlertManager:
    def local_alert()      # winsound beep
    def telegram_alert()   # API Telegram async
    def whatsapp_hook()   # Webhook POST placeholder
    def send_all_alerts() # Envía a todos los canales
```

### 3. calibrate.py
- Seleccionar área de pantalla con mouse
- Capturar template de referencia
- Analizar color promedio (HEX)
- Guardar coordenadas en .env

### 4. sentinel.pyw
- **Detección**: Color matching + Template matching
- **_polling**: Random 45-90 segundos
- **Auto-kill**: Detecta Hubstaff activo
- **DPI Awareness**: SetProcessDpiAwareness(1)

---

## Uso

### 1. Calibración (primera vez)
```bash
python calibrate.py
```
- Ejecutar con Hubstaff abierto
- Seleccionar área del presupuesto rojo
- Se genera `templates/budget_red.png`
- Se guardan coordenadas en `.env`

### 2. Ejecutar Monitor
```bash
pythonw sentinel.pyw
```
- Ejecución sin consola (`.pyw`)
- Intervalo aleatorio entre verificaciones

### 3. Configurar Notificaciones
Editar `.env`:
```
TELEGRAM_TOKEN=123456:ABCDEF...
TELEGRAM_CHAT_ID=123456789
WHATSAPP_WEBHOOK_URL=https://...
```

---

## Parámetros .env

| Parámetro | Default | Descripción |
|-----------|---------|-------------|
| TELEGRAM_TOKEN | - | Token bot Telegram |
| TELEGRAM_CHAT_ID | - | Chat ID destino |
| WHATSAPP_WEBHOOK_URL | - | Webhook WhatsApp |
| CHECK_INTERVAL_MIN | 45 | Mínimo segundos |
| CHECK_INTERVAL_MAX | 90 | Máximo segundos |
| CONSECUTIVE_FAILURES | 3 | Fallos para alerta |
| CALIBRATION_X | 0 | Coordenada X |
| CALIBRATION_Y | 0 | Coordenada Y |
| CALIBRATION_W | 200 | Ancho región |
| CALIBRATION_H | 100 | Alto región |
| RED_COLOR_HEX | #FF0000 | Color a detectar |

---

## Lógica de Detección

```
1. Capturar región calibrada (x, y, w, h)
2. Detectar color rojo (tolerancia ±30)
3. Comparar con template (match > 0.7)
4. Si NO se detecta rojo por 3 ciclos → ALERTA
5. Si Hubstaff activo → AUTO-KILL
```

---

## Requisitos

```bash
pip install pyautogui opencv-python numpy python-dotenv pywin32 aiohttp requests
```

---

## Rendimiento

- **CPU**: ~1-2% (intervalo amplio, operaciones simples)
- **Memoria**: ~50MB
- **Consola**: Oculta (ejecución .pyw)

---

## DPI Scaling

El módulo fuerza `SetProcessDpiAwareness(1)` para que las coordenadas de pyautogui coincidan con el escalado de Windows (125%, 150%).

---

## Arquitectura de Alertas (Extensible)

```python
class AlertManager:
    local_alert()    # winsound - siempre disponible
    telegram_alert() # async vía aiohttp
    whatsapp_hook() # POST webhook (placeholder)
```

---

## Excepciones

- Ventana minimizada: Retry automático
- Captura fallida: Incrementar contador de fallos
- Hubstaff cubierto: Logging + continue

---

# VERSIÓN 1.1 - Actualización

## Nuevas Características

### 1. Alarma Nuclear
Reemplaza el pitido simple con `disparar_alarma_nuclear()`:
- Alterna frecuencias **2500Hz** y **1500Hz**
- 10 iteraciones en bucle
- Sonido imposible de ignorar

```python
def disparar_alarma_nuclear(self):
    frequencies = [2500, 1500]
    for i in range(10):
        freq = frequencies[i % 2]
        winsound.Beep(freq, duration)
```

### 2. Anti-Falsos Positivos
- **Confidence**: 0.9 (antes 0.7)
- **Grayscale**: True (ignora variaciones de brillo)
- **Validación**: 3 ciclos consecutivos de ausencia
- **Debug Screenshots**: Cada intento/alerta se guarda

### 3. Modo Test (`--test`)
Argumento para validar funcionalidad:
```bash
python sentinel.pyw --test
```
Secuencia:
1. Dispara alarma nuclear
2. Envía mensaje de prueba a Telegram
3. Simulación completada

### 4. Debug Screenshots
Carpeta `debug_captures/` con capturas:
- `debug_attempt_N.png` - Cada intento de detección
- `debug_capture_fail.png` - Fallo de captura
- `debug_inconclusive.png` - Dete inconclusive

### 5. Logging Mejorado
Muestra estado del contador en cada ciclo:
```
Budget disponible detectado? (1/3)
Budget disponible detectado? (2/3)
>>> 🚨 PRESUPUESTO DISPONIBLE DETECTADO 🚨 <<<
```

---

## Credenciales Telegram (Hardcoded v1.1)

| Variable | Valor |
|----------|-------|
| TOKEN | `8641310141:AAHq4DNM-zmJMS7PwD35lRwpLK8SdeamCZM` |
| CHAT_ID | `7239466863` |

---

## Parámetros de Detección v1.1

| Parámetro | Valor v1.0 | Valor v1.1 |
|-----------|------------|------------|
| Template Confidence | 0.7 | **0.9** |
| Color Matching | RGB | **Grayscale** |
| Validación ciclos | 3 | 3 (confirmado) |
| Debug Screenshots | No | **Sí** |
| Alarma | Simple Beep | **Alarma Nuclear** |
| Modo Test | No | **Sí** |

---

## Uso v1.1

### Ejecutar monitor:
```bash
pythonw sentinel.pyw
```

### Modo test:
```bash
python sentinel.pyw --test
```

### Modo monitor (debug):
```bash
python sentinel.pyw --monitor
```

### Modo calibracion visual:
```bash
python sentinel.pyw --calibrate
```

### Ver logs:
```bash
type sentinel.log
```

---

## Changelog v1.1

- ✅ Alarm nuclear implementada
- ✅ Confidence 0.9 con grayscale
- ✅ Debug screenshots activados
- ✅ Modo --test agregado
- ✅ Logging mejorado con contador
- ✅ Credenciales hardcodeadas en alerts.py
- ✅ Carpeta debug_captures/ creada

---

# VERSIÓN 1.2 - "The Nuclear Update"

## Nuevas Características

### 1. Twilio - Timbrazo Telefónico
Llamada automática que timbrea 15 segundos:
- **API Key**: `XXXXX`
- **SID**: `XXXXX`
- **Desde**: `+51XXXXX`
- **Hacia**: `+51XXXXX`
- Auto-colgado antes del buzón (status='completed')

```python
def twilio_call_timbrazgo(self):
    call = client.calls.create(to=TO, from_=FROM, url=twimlet)
    time.sleep(15)
    call.update(status='completed')
```

### 2. Contador con Reset
Lógica anti-falsos positivos mejorada:
- Si detectarojo en ciclo 1/3 → Contador **REINICIADO** a 0
- Solo alerta si **3 ciclos seguidos** sin rojo

```
[INFO] Ciclo 1/3: Rojo no detectado. Esperando confirmación...
[INFO] Ciclo 2/3: Rojo no detectado. Esperando confirmación...
>>> 🚨 PRESUPUESTO DISPONIBLE DETECTADO (3/3) 🚨 <<<
```

### 3. Secuencia de Asalto Completa
Cuando se confirma disponibilidad (3/3):
1. Alarma Nuclear (winsound 2500/1500Hz)
2. Telegram con mensaje + screenshot
3. Twilio timbrazo (15 segundos)

### 4. Modo Test v1.2
```bash
python sentinel.py --test
```
Secuencia:
1. Alarma nuclear
2. Telegram test
3. Twilio timbrazo
4. Completado

### 5. Debug Screenshots Mejorados
- Cada intento guarda captura con timestamp
- Screenshot final se adjunta a Telegram

---

## Comparación v1.0 vs v1.1 vs v1.2

| Característica | v1.0 | v1.1 | v1.2 |
|---------------|------|------|------|
| Template Confidence | 0.7 | 0.9 | 0.9 |
| Grayscale | No | Sí | Sí |
| Contador Reset | No | No | **Sí** |
| Alarma Nuclear | Simple | Sí | Sí |
| Telegram | Sí | Sí | Sí |
| Twilio | No | No | **Sí** |
| Debug Screens | No | Sí | Sí |
| Modo Test | No | Sí | Sí |

---

## Uso v1.2

### Ejecutar monitor:
```bash
pythonw sentinel.pyw
```

### Modo test:
```bash
python sentinel.pyw --test
```

### Ver logs:
```bash
type sentinel.log
```

---

## Changelog v1.2

- ✅ Twilio timbrazo implementado
- ✅ Contador con reset si reaparece el rojo
- ✅ Secuencia de asalto: Sonido + Telegram + Twilio
- ✅ Logging mejorado con mensajes claros
- ✅ Debug screenshots con timestamp
- ✅ Requiere: `pip install twilio`

---

## Modo INVERSE v1.3

El modo INVERSE invierte la lógica de detección:

| Modo | Detecta | Alerta cuando |
|------|---------|---------------|
| NORMAL | ROJO | ROJO **desaparece** (presupuesto disponible) |
| INVERSE | GRIS | GRIS **desaparece** (presupuesto agotado = rojo visible) |

### Comportamiento INVERSE:
1. Si detecta GRIS → Reset contador (estado normal, gris presente)
2. Si NO detecta GRIS → Incrementa ciclo (gris desapareció = alerta)
3. Después de 3 ciclos sin GRIS → **ALERTA!**

### Configuración en .env:

```env
DETECTION_MODE=INVERSE
GREY_COLOR_HEX=#6B7280
```

- `DETECTION_MODE=NORMAL` → Detección estándar (Rojo)
- `DETECTION_MODE=INVERSE` → Detección inversa (Gris)

### Parámetros de Detección v1.3:

| Parámetro | Valor v1.2 | Valor v1.3 |
|-----------|------------|------------|
| DETECTION_MODE | NORMAL | NORMAL/INVERSE |
| TEMPLATE_CONFIDENCE | 0.9 (hardcoded) | 0.0-1.0 (configurable) |
| COLOR_RATIO_THRESHOLD | 0.15 (hardcoded) | 0.0-1.0 (configurable) |
| RED_COLOR_HEX | #C9292F | #C9292F |
| RED_TEMPLATE_PATH | templates/budget_red.png | templates/budget_red.png |
| GREY_COLOR_HEX | - | #6B7280 |
| GREY_TEMPLATE_PATH | - | templates/budget_grey.png |
| VERIFICACION_HUBSTAFF | ENABLED | DISABLED/ENABLED |
| TWILIO_BURST_CALLS | 1 | 3 (configurable) |
| TWILIO_TIME_CALLOUT | 15 | 20 (configurable) |
| TWILIO_TIME_TO_MAKE_CALL | - | 10 (configurable) |

## Comparación v1.0 vs v1.1 vs v1.2 vs v1.3

| Característica | v1.0 | v1.1 | v1.2 | v1.3 |
|----------------|------|------|------|------|
| Detección color | ✅ | ✅ | ✅ | ✅ |
| Template matching | ✅ | ✅ | ✅ | ✅ |
| Telegram alerts | ✅ | ✅ | ✅ | ✅ |
| Twilio calls | - | - | ✅ | ✅ |
| Alarm sonido | - | ✅ | ✅ | ✅ |
| Modo INVERSE | - | - | - | ✅ |
| Grayscale | - | ✅ | ✅ | ✅ |
| 3 ciclos validación | - | ✅ | ✅ | ✅ |
| Ráfaga timbrazgos | - | - | - | ✅ |
| Verificacion Hubstaff | ✅ | ✅ | ✅ | ✅ (configurable) |

## Uso v1.3

### Modo normal (Rojo):
```env
DETECTION_MODE=NORMAL
```
```bash
python sentinel.pyw
```

### Modo inverse (Gris):
```env
DETECTION_MODE=INVERSE
GREY_COLOR_HEX=#6B7280
```
```bash
python sentinel.pyw
```

### Modo test:
```bash
python sentinel.pyw --test
```

### Ver logs:
```bash
type sentinel.log
```

---

## Changelog v1.3

- ✅ Modo INVERSE implementado y corregido
- ✅ Detección de GRIS cuando desaparece
- ✅ INVERSE: Si NO detecta GRIS → Incrementa ciclo (no reset)
- ✅ Nueva variable GREY_COLOR_HEX y GREY_TEMPLATE_PATH
- ✅ DETECTION_MODE en .env (NORMAL/INVERSE)
- ✅ VERIFICACION_HUBSTAFF configurables en .env
- ✅ Ráfaga de timbrazgos Twilio (hasta 3 llamadas)
- ✅ TWILIO_BURST_CALLS, TWILIO_TIME_CALLOUT, TWILIO_TIME_TO_MAKE_CALL configurables en .env
- ✅ Try-except en call.update() para evitar errores si la llamada ya fue finalizada
- ✅ Logging detallado con [DETECCION] y [TWILIO]
- ✅ Flag --monitor para debug con screenshots cada ciclo
- ✅ Flag --calibrate para calibración visual interactiva
- ✅ Selector de región con drag de mouse en modo calibración