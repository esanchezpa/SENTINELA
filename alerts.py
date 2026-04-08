import winsound
import asyncio
import aiohttp
import requests
import time
from datetime import datetime
import logging

from config import CONFIG

TELEGRAM_TOKEN = CONFIG.get("telegram_token", "")
TELEGRAM_CHAT_ID = CONFIG.get("telegram_chat_id", "")

TWILIO_API_KEY = CONFIG.get("twilio_api_key", "")
TWILIO_SID = CONFIG.get("twilio_sid", "")
TWILIO_ACCOUNT_SID = CONFIG.get("twilio_account_sid", "")
TWILIO_AUTH_TOKEN = CONFIG.get("twilio_auth_token", "")
TWILIO_FROM = CONFIG.get("twilio_from", "")
TWILIO_TO = CONFIG.get("twilio_to", "")
TWILIO_TEST_SID = CONFIG.get("twilio_test_sid", "")
TWILIO_TEST_AUTH_TOKEN = CONFIG.get("twilio_test_auth_token", "")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class AlertManager:
    def __init__(self, enable_telegram=True, enable_twilio=True):
        self.enable_telegram = enable_telegram
        self.enable_twilio = enable_twilio
        self.token = TELEGRAM_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        
    def disparar_alarma_nuclear(self):
        logger.info(">>> ALARMA NUCLEAR ACTIVADA <<<")
        frequencies = [2500, 1500]
        for i in range(10):
            freq = frequencies[i % 2]
            duration = 200 if i % 2 == 0 else 300
            try:
                winsound.Beep(freq, duration)
            except Exception as e:
                logger.error(f"Error en alarma nuclear: {e}")
            time.sleep(0.1)
        logger.info(">>> ALARMA NUCLEAR FINALIZADA <<<")

    async def _send_telegram_async(self, message: str, image_path: str = None):
        if not self.token or not self.chat_id:
            logger.warning("Telegram no configurado")
            return False
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        data = {"chat_id": self.chat_id, "text": message}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    success = resp.status == 200
                    logger.info(f"Telegram respuesta: {resp.status}")
                    return success
        except Exception as e:
            logger.error(f"[TELEGRAM] Error: {e}")
            return False

    def telegram_alert(self, message: str, image_path: str = None):
        if not self.enable_telegram:
            return
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.run_until_complete(self._send_telegram_async(message, image_path))

    def twilio_call_timbrazgo(self):
        if not self.enable_twilio:
            logger.warning("Twilio deshabilitado")
            return False
        
        from config import CONFIG
        burst_calls = CONFIG.get("twilio_burst_calls", 3)
        time_callout = CONFIG.get("twilio_time_callout", 20)
        time_to_make_call = CONFIG.get("twilio_time_to_make_call", 10)
        
        use_test = bool(TWILIO_TEST_SID and TWILIO_TEST_AUTH_TOKEN)
        if use_test:
            account_sid = TWILIO_TEST_SID
            auth_token = TWILIO_TEST_AUTH_TOKEN
            logger.info("[TWILIO] Usando credenciales de TEST")
        else:
            if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
                logger.error("[TWILIO] TWILIO_ACCOUNT_SID o TWILIO_AUTH_TOKEN no configurado en .env")
                return False
            account_sid = TWILIO_ACCOUNT_SID
            auth_token = TWILIO_AUTH_TOKEN
            logger.info("[TWILIO] Usando credenciales LIVE")
        
        try:
            from twilio.rest import Client
            client = Client(account_sid, auth_token)
            
            api_url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Calls.json"
            logger.info(f"[TWILIO] URL API: {api_url}")
            logger.info(f"[TWILIO] From: {TWILIO_FROM} -> To: {TWILIO_TO}")
            
            for attempt in range(1, burst_calls + 1):
                logger.info(f"[TWILIO] Lanzando timbrazo {attempt} de {burst_calls}...")
                
                try:
                    call = client.calls.create(
                        to=TWILIO_TO,
                        from_=TWILIO_FROM,
                        url="http://twimlets.com/holdmusic?Bucket=com.twilio.music.ambient"
                    )
                    
                    logger.info(f"Llamada {attempt} iniciada SID: {call.sid}")
                    time.sleep(time_callout)
                    
                    try:
                        call.update(status="completed")
                        logger.info(f"Llamada {attempt} finalizada (timbrazgo completado)")
                    except Exception as update_err:
                        logger.warning(f"Llamada {attempt} ya finalizada o no necesita update: {update_err}")
                    
                    if attempt < burst_calls:
                        logger.info(f"[TWILIO] Esperando {time_to_make_call}s antes del siguiente timbrazo...")
                        time.sleep(time_to_make_call)
                        
                except Exception as call_err:
                    logger.error(f"[TWILIO] Error en timbrazo {attempt}: {call_err}")
                    if attempt < burst_calls:
                        time.sleep(time_to_make_call)
                    continue
            
            logger.info("[TWILIO] Secuencia de timbrazgos completada")
            return True
            
        except Exception as e:
            logger.error(f"[TWILIO] Error general en timbrazgo: {e}")
            return False

    def send_all_alerts(self, message: str, image_path: str = None):
        self.disparar_alarma_nuclear()
        self.telegram_alert(message, image_path)
        self.twilio_call_timbrazgo()

    def test_mode(self):
        logger.info("=== MODO SIMULADOR v1.3 ===")
        logger.info("1/4 - Disparando alarma nuclear...")
        self.disparar_alarma_nuclear()
        
        logger.info("2/4 - Enviando mensaje de prueba a Telegram...")
        self.telegram_alert("🔔 TEST v1.3 - Sentinel funcionando correctamente")
        
        logger.info("3/4 - Ejecutando timbrazo Twilio...")
        self.twilio_call_timbrazgo()
        
        logger.info("4/4 - Simulacion completada")
        logger.info("=== TEST v1.3 FINALIZADO ===")