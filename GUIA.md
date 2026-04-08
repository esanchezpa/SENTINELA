# Guía de Uso - Sentinel

## Primer Uso

### 1. Instalar Dependencias

```bash
pip install pyautogui opencv-python numpy python-dotenv pywin32 aiohttp requests
```

---

### 2. Ejecutar Calibración

1. Abre Hubstaff en tu PC
2. Asegúrate de ver el estado "Budget Agotado" (rojo) o "Multiple limits"
3. Ejecuta en terminal:
   ```bash
   python calibrate.py
   ```
4. El script te pedira coordenadas de la region a monitorear
   - Si tienes el área visible, ingresa las coordenadas X, Y, W, H
   - Si no, usa el mouse para localizar la posición y anota las coordenadas

---

### 3. Obtener Coordenadas (Tips)

**Opción A - Manual:**
- Presiona `Win + Shift + S` en Windows
- Arrastra para seleccionar el área del presupuesto
- Las coordenadas aparecen en la notificación

**Opción B - Script:**
- minimiza todas las ventanas
- Ejecuta `python -c "import pyautogui; print(pyautogui.position())"`
- Move el mouse al área del presupuesto y anota posición

---

### 4. Guardar Configuración

Edita el archivo `.env` con los valores obtenidos:

```
CALIBRATION_X=123
CALIBRATION_Y=456
CALIBRATION_W=200
CALIBRATION_H=80
RED_COLOR_HEX=#FF0000
```

---

### 5. Verificar Template

El script `calibrate.py` debe crear:
```
templates/budget_red.png
```

Si no se creó, puedes手动mente guardar una captura:
```python
import pyautogui
img = pyautogui.screenshot(region=(X, Y, W, H))
img.save("templates/budget_red.png")
```

---

### 6. Iniciar Monitor

```bash
pythonw sentinel.pyw
```

- NO habrá ventana de consola
- Verifica en `sentinel.log` que inició correctamente

---

## Tips

### DPI Scaling

Si las coordenadas no coinciden:
- Verifica el nivel de escalado en Windows (Configuración → Pantalla → Escala)
- Ajusta las coordenadas multiplicando por el factor de escala
  - 125% → multiplicar por 1.25
  - 150% → multiplicar por 1.50

### Detección Falsa

Aumenta `CONSECUTIVE_FAILURES` en `.env`:
```
CONSECUTIVE_FAILURES=5
```

O aumenta la tolerancia del color en `sentinel.pyw`:
```python
lower = np.array([max(0, r-50), max(0, g-50), max(0, b-50)])  # ±50 en vez de ±30
```

### Detección No Activa

Reduce el intervalo mínimo:
```
CHECK_INTERVAL_MIN=30
CHECK_INTERVAL_MAX=60
```

### Apagar Monitor

- Mata el proceso desde Administrador de Tareas
- O crea un archivo `stop_sentinel` para apagado seguro

---

## Troubleshooting

| Error | Solución |
|-------|---------|
| Coordenadas incorrectas | Ajusta CALIBRATION_* en .env |
| Template no encontrado | Verifica `templates/budget_red.png` existe |
| Hubstaff no detectado | Verifica el nombre de ventana contiene "hubstaff" |
| Telegram no envía | Verifica TOKEN y CHAT_ID en .env |
| CPU alto | Aumenta intervalos en .env |

---

## Configuración Avanzada

### Telegram

1. Chatea con @BotFather en Telegram
2. Crea un nuevo bot: `/newbot`
3. Copia el token (ej: `123456:ABC-DEF`)
4. Chatea con @userinfobot para obtener tu Chat ID

### WhatsApp Webhook

Introduce la URL de tu webhook en:
```
WHATSAPP_WEBHOOK_URL=https://tu-servidor.com/webhook
```

---

## Iniciar con Windows

Para iniciar automáticamente:

1. Crea un archivo `.bat`:
   ```bat
   @echo off
   pythonw "C:\...\sentinel.pyw"
   ```
2. Presiona `Win + R`, escribe `shell:startup`
3. Arrastra el archivo .bat a la carpeta de inicio

---

# GUÍA v1.1 - Nuevas Características

## Modo Test

Para validar que todo funciona:

```bash
python sentinel.pyw --test
```

Esto ejecutará:
1. Alarma nuclear (sonido)
2. Mensaje de prueba a Telegram
3. Confirmación en log

## Debug Screenshots

Cuando el script detecte cambios, guardará capturas en:
```
debug_captures/
├── debug_attempt_1_20240406_143022.png
├── debug_attempt_2_20240406_143107.png
└── debug_attempt_3_20240406_143152.png
```

Útil para analizar falsos positivos.

## Ver Logs en Tiempo Real

```bash
type sentinel.log
```

O abre el archivo directamente en el editor.

## Parámetros v1.1

| Ajuste | Valor | Efecto |
|--------|-------|--------|
| Confidence | 0.9 | Más estricto, menos falsos positivos |
| Grayscale | True | Ignora variaciones de brillo |
| Alarma | Nuclear | Sonido imposible de ignorar |

## Actualizar a v1.1

Si tienes la versión anterior:
1. Reemplaza `sentinel.pyw` con el nuevo
2. Reemplaza `alerts.py` con el nuevo
3. Ejecuta `python sentinel.pyw --test` para verificar

---

# GUÍA v1.2 - "The Nuclear Update"

## Nuevas Características

### Twilio - Timbrazo Telefónico
El script ahora puede llamar a tu teléfono cuando se detecta disponibilidad:
- Timbrea durante 15 segundos
- Se cuelga automáticamente (antes del buzón)
- Configuración en `alerts.py` (hardcodeada)

### Contador con Reset
- Si el rojo reaparece después de un intento, el contador **se reinicia**
- Solo alerta cuando hay **3 ciclos seguidos** sin detección

### Secuencia de Asalto Completa
Al detectar disponibilidad (3/3):
1. Alarma nuclear (sonido)
2. Mensaje Telegram con screenshot
3. Llamada Twilio (timbrazgo)

## Instalar Dependencia Twilio

```bash
pip install twilio
```

## Modo Test v1.2

```bash
python sentinel.pyw --test
```

Ejecuta la secuencia completa:
1. Alarma nuclear
2. Telegram test
3. Twilio timbrazo (llamada real)

## Solución de Problemas v1.2

| Error | Solución |
|-------|----------|
| Twilio no conecta | Verificar API Key y SID |
| Llamada no entra | Verificar número destino |
| Modo test funciona pero detección no | Verificar coordenadas en .env |

# GUÍA v1.3 - Modo INVERSE

## ¿Qué es el Modo INVERSE?

El modo INVERSE invierte la lógica de detección:

| Modo | Detecta | Alerta cuando |
|------|---------|---------------|
| NORMAL | ROJO | ROJO **desaparece** (presupuesto disponible) |
| INVERSE | GRIS | GRIS **desaparece** (presupuesto agotado = rojo visible) |

### Comportamiento INVERSE:
1. Si detecta GRIS → Reset contador (estado normal, gris presente)
2. Si NO detecta GRIS → Incrementa ciclo (gris desapareció = alerta)
3. Después de 3 ciclos sin GRIS → **ALERTA!**

## Nuevas Variables .env

```env
DETECTION_MODE=NORMAL
RED_COLOR_HEX=#C9292F
RED_TEMPLATE_PATH=templates/budget_red.png
GREY_COLOR_HEX=#6B7280
GREY_TEMPLATE_PATH=templates/budget_grey.png
```

### Parámetros v1.3

| Variable | Descripción | Valores |
|----------|-------------|---------|
| DETECTION_MODE | Modo de detección | NORMAL (rojo) / INVERSE (gris) |
| TEMPLATE_CONFIDENCE | Similitud mínima del template | 0.0-1.0 (default: 0.9) |
| COLOR_RATIO_THRESHOLD | Porcentaje mínimo de color | 0.0-1.0 (default: 0.15) |
| RED_COLOR_HEX | Color hexadecimal del rojo | #C9292F (default) |
| RED_TEMPLATE_PATH | Template para modo NORMAL | templates/budget_red.png |
| GREY_COLOR_HEX | Color hexadecimal del gris | #6B7280 (default) |
| GREY_TEMPLATE_PATH | Template para modo INVERSE | templates/budget_grey.png |
| VERIFICACION_HUBSTAFF | Verificar si Hubstaff está activo | ENABLED / DISABLED |

## Configuración para Modo INVERSE

1. Establecer DETECTION_MODE=INVERSE
2. Configurar GREY_COLOR_HEX=#6B7280
3. Colocar template gris en templates/budget_grey.png

## Ejemplo de Uso

### Modo NORMAL (Rojo):
```env
DETECTION_MODE=NORMAL
RED_COLOR_HEX=#C9292F
```

### Modo INVERSE (Gris):
```env
DETECTION_MODE=INVERSE
GREY_COLOR_HEX=#6B7280
```

## Actualizar a v1.3

No se requieren nuevas dependencias. Solo actualizar archivos:
- sentinel.pyw
- config.py
- .env (agregar nuevas variables)
- GUIA.md (este archivo)
- PLAN.md

## Solución de Problemas v1.3

| Problema | Solución |
|----------|----------|
| No detecta gris | Verificar GREY_COLOR_HEX correcto |
| Modo inverse no funciona | Verificar DETECTION_MODE=INVERSE |
| Alerta cuando aparece gris | Verificar que sea modo NORMAL |

# GUÍA v1.3 - Ráfaga de Timbrazgos Twilio

## ¿Qué es la Ráfaga de Timbrazgos?

La ráfaga de timbrazgos realiza múltiples llamadas consecutivas para asegurar que el usuario sea alertado, especialmente si el teléfono está en modo silencio o no contesta la primera llamada.

## Variables de Configuración .env

```env
TWILIO_BURST_CALLS=3
TWILIO_TIME_CALLOUT=20
TWILIO_TIME_TO_MAKE_CALL=10
```

| Variable | Descripción | Valor Default |
|----------|-------------|---------------|
| TWILIO_BURST_CALLS | Cantidad de timbrazgos a realizar | 3 |
| TWILIO_TIME_CALLOUT | Segundos de espera antes de finalizar cada llamada | 20 |
| TWILIO_TIME_TO_MAKE_CALL | Segundos de espera entre timbrazgos | 10 |

## Ejemplo de Configuración

### Configuración Agresiva (más timbrazgos, menos espera):
```env
TWILIO_BURST_CALLS=5
TWILIO_TIME_CALLOUT=15
TWILIO_TIME_TO_MAKE_CALL=5
```

### Configuración Conservadora (menos timbrazgos, más espera):
```env
TWILIO_BURST_CALLS=2
TWILIO_TIME_CALLOUT=25
TWILIO_TIME_TO_MAKE_CALL=15
```

## Flujo de Ejecución

1. Lanzar timbrazo 1 de 3
2. Esperar 20 segundos (TIME_CALLOUT)
3. Finalizar llamada (call.update)
4. Esperar 10 segundos (TIME_TO_MAKE_CALL)
5. Lanzar timbrazo 2 de 3
6. ... (repetir hasta completar)

## Solución de Problemas v1.3 - Twilio Burst

| Problema | Solución |
|----------|----------|
| Operadora bloquea números | Aumentar TWILIO_TIME_TO_MAKE_CALL |
| Muchas llamadas gratuitas gastadas | Reducir TWILIO_BURST_CALLS |
| Llamadas se cortan antes de timbrar | Reducir TWILIO_TIME_CALLOUT |
| Error en call.update | Normal, la llamada ya fue finalizada |

---

# GUÍA v1.3 - Flags de Línea de Comandos

## Flags Disponibles

| Flag | Descripción |
|------|-------------|
| `--test` | Simula las alertas sin hacer detección real |
| `--calibrate` | Modo calibración visual interactiva |
| `--monitor` | Modo debug con screenshots cada ciclo (10s) |

## Uso de --test

```bash
python sentinel.pyw --test
```
Ejecuta la secuencia de alertas (alarma + Telegram + Twilio) sin monitorear.

## Uso de --calibrate

```bash
python sentinel.pyw --calibrate
```
Abre un menú interactivo:
- **Opción 1**: Ver región actual (screenshot con rectángulo verde)
- **Opción 2**: Recalibrar - dibujar nueva región con click + arrastrar
- **Opción 3**: Salir

### Controles del selector:
- **Click + Arrastrar**: Dibujar rectángulo
- **S**: Confirmar selección
- **Q**: Cancelar

## Uso de --monitor

```bash
python sentinel.pyw --monitor
```
Modo debug que:
- Captura screenshot cada 10 segundos
- Guarda en `debug_captures/monitor_TIMESTAMP.png`
- Muestra logs detallados de detección [DETECCION]

## Ejecución Normal

```bash
python sentinel.pyw
```
Modo de monitoreo estándar con verificación cada 45-90 segundos.
