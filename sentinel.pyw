import os
import sys
import time
import random
import ctypes
import logging
import win32gui
import argparse
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent.resolve()

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

import pyautogui
import cv2
import numpy as np
from config import CONFIG
from alerts import AlertManager

DEBUG_DIR = Path("debug_captures")
DEBUG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(SCRIPT_DIR / "sentinel.log", encoding="utf-8", mode='a'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

drawing = {"start_x": None, "start_y": None, "image": None, "temp_image": None, "done": False}

def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing["start_x"] = x
        drawing["start_y"] = y
        drawing["temp_image"] = drawing["image"].copy()
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing["start_x"] is not None:
            img = drawing["image"].copy()
            cv2.rectangle(img, (drawing["start_x"], drawing["start_y"]), (x, y), (0, 255, 0), 2)
            cv2.imshow("Sentinel - Calibracion", img)
    elif event == cv2.EVENT_LBUTTONUP:
        if drawing["start_x"] is not None:
            end_x, end_y = x, y
            sx, sy = drawing["start_x"], drawing["start_y"]
            drawing["image"].fill(0)
            cv2.rectangle(drawing["image"], (sx, sy), (end_x, end_y), (0, 255, 0), 3)
            text = f"X:{sx} Y:{sy} W:{abs(end_x-sx)} H:{abs(end_y-sy)}"
            cv2.putText(drawing["image"], text, (sx, sy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            drawing["temp_image"] = drawing["image"].copy()
            cv2.imshow("Sentinel - Calibracion", drawing["image"])
            drawing["start_x"] = None
            drawing["start_y"] = None

def show_calibration_region():
    print("Capturando pantalla en 3... 2... 1...")
    time.sleep(1)
    screenshot = pyautogui.screenshot()
    drawing["image"] = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    x = CONFIG["calibration_x"]
    y = CONFIG["calibration_y"]
    w = CONFIG["calibration_w"]
    h = CONFIG["calibration_h"]
    
    cv2.rectangle(drawing["image"], (x, y), (x + w, y + h), (0, 255, 0), 3)
    cv2.putText(drawing["image"], "AREA SENTINEL", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(drawing["image"], f"X:{x} Y:{y} W:{w} H:{h}", (x, y + h + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    
    cv2.namedWindow("Sentinel - Calibracion")
    cv2.setMouseCallback("Sentinel - Calibracion", mouse_callback)
    cv2.imshow("Sentinel - Calibracion", drawing["image"])
    print("Ventana abierta. Presiona 'Q' para cerrar o 'S' para seleccionar region...")

def save_calibration(x, y, w, h):
    with open(SCRIPT_DIR / ".env", "r") as f:
        lines = f.readlines()
    
    new_lines = []
    for line in lines:
        if line.startswith("CALIBRATION_X="):
            new_lines.append(f"CALIBRATION_X={x}\n")
        elif line.startswith("CALIBRATION_Y="):
            new_lines.append(f"CALIBRATION_Y={y}\n")
        elif line.startswith("CALIBRATION_W="):
            new_lines.append(f"CALIBRATION_W={w}\n")
        elif line.startswith("CALIBRATION_H="):
            new_lines.append(f"CALIBRATION_H={h}\n")
        else:
            new_lines.append(line)
    
    with open(SCRIPT_DIR / ".env", "w") as f:
        f.writelines(new_lines)
    
    from config import load_config
    global CONFIG
    CONFIG = load_config()
    print(f"Coordenadas guardadas: X={x}, Y={y}, W={w}, H={h}")

def run_visual_calibration():
    while True:
        print("\n" + "=" * 50)
        print("=== SENTINEL - CALIBRACION VISUAL ===")
        print("=" * 50)
        print(f"Region actual: X={CONFIG['calibration_x']}, Y={CONFIG['calibration_y']}, W={CONFIG['calibration_w']}, H={CONFIG['calibration_h']}")
        print()
        print("1. Ver region actual")
        print("2. Recalibrar (nueva region)")
        print("3. Salir")
        print()
        opcion = input("Selecciona una opcion (1/2/3): ").strip()
        
        if opcion == "1":
            show_calibration_region()
            while True:
                key = cv2.waitKey(100) & 0xFF
                if key == ord('q') or key == 27:
                    break
            cv2.destroyAllWindows()
        elif opcion == "2":
            drawing["temp_image"] = None
            show_calibration_region()
            print("\nDibujar region: Click + Arrastrar")
            print("Presiona 'S' para confirmar o 'Q' para cancelar...")
            
            while True:
                key = cv2.waitKey(100) & 0xFF
                if key == ord('q') or key == 27:
                    print("Cancelado.")
                    break
                elif key == ord('s'):
                    if drawing["temp_image"] is not None:
                        img = drawing["temp_image"].copy()
                        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                        contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                        
                        if contours:
                            bx, by, bw, bh = cv2.boundingRect(contours[0])
                            print(f"\nRegion seleccionada: X={bx}, Y={by}, W={bw}, H={bh}")
                            
                            import tkinter as tk
                            from tkinter import messagebox
                            root = tk.Tk()
                            root.withdraw()
                            root.attributes("-topmost", True)
                            respuesta = messagebox.askyesno("Confirmar Region", f"Guardar region?\n\nX={bx}, Y={by}, W={bw}, H={bh}")
                            
                            if respuesta:
                                save_calibration(bx, by, bw, bh)
                                print("Region guardada exitosamente!")
                            else:
                                print("Region descartada.")
                            root.destroy()
                    else:
                        print("No se selecciono ninguna region. Haz click y arrastra primero.")
                    break
            
            cv2.destroyAllWindows()
        elif opcion == "3":
            print("Saliendo del modo calibracion...")
            break
        else:
            print("Opcion no valida. Intenta de nuevo.")
    
    sys.exit(0)

class SentinelMonitor:
    def __init__(self):
        self.config = CONFIG
        self.alert_manager = AlertManager()
        self.cycle_count = 0
        self.detection_threshold = self.config["consecutive_failures"]
        self.running = True
        self.hubstaff_active = False
        self.last_debug_path = None
        self.detection_mode = self.config.get("detection_mode", "NORMAL")
        
    def get_hubstaff_window_state(self):
        try:
            def callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if "hubstaff" in title.lower():
                        windows.append({
                            "hwnd": hwnd,
                            "title": title,
                            "minimized": win32gui.IsIconic(hwnd)
                        })
                return True
            
            windows = []
            win32gui.EnumWindows(callback, windows)
            
            for win in windows:
                if not win["minimized"]:
                    self.hubstaff_active = True
                    logger.info(f"Hubstaff detectado: {win['title']}")
                    return True
            
            self.hubstaff_active = False
            return False
            
        except Exception as e:
            logger.debug(f"Error verificando ventana: {e}")
            return None

    def save_debug_screenshot(self, reason: str):
        try:
            x = self.config["calibration_x"]
            y = self.config["calibration_y"]
            w = self.config["calibration_w"]
            h = self.config["calibration_h"]
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"debug_{reason}_{timestamp}.png"
            filepath = DEBUG_DIR / filename
            
            screenshot = pyautogui.screenshot(region=(x, y, w, h))
            screenshot.save(filepath)
            logger.info(f"Screenshot debug guardado: {filepath}")
            self.last_debug_path = str(filepath)
            return str(filepath)
        except Exception as e:
            logger.error(f"Error guardando screenshot debug: {e}")
            return None

    def capture_region(self):
        x = self.config["calibration_x"]
        y = self.config["calibration_y"]
        w = self.config["calibration_w"]
        h = self.config["calibration_h"]
        
        try:
            screenshot = pyautogui.screenshot(region=(x, y, w, h))
            return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        except Exception as e:
            logger.error(f"Error capturando region: {e}")
            return None

    def detect_budget_blocked(self, image):
        if image is None:
            return None
        
        mode = self.detection_mode
        target_hex = self.config["red_color_hex" if mode == "NORMAL" else "grey_color_hex"].upper()
        
        try:
            r = int(target_hex[1:3], 16)
            g = int(target_hex[3:5], 16)
            b = int(target_hex[5:7], 16)
            
            lower = np.array([max(0, r-30), max(0, g-30), max(0, b-30)])
            upper = np.array([min(255, r+30), min(255, g+30), min(255, b+30)])
            
            mask = cv2.inRange(image, lower, upper)
            color_ratio = cv2.countNonZero(mask) / (image.shape[0] * image.shape[1])
            color_thresh = self.config.get("color_ratio_threshold", 0.15)
            logger.info(f"[DETECCION] Color ratio: {color_ratio:.3f} (threshold: {color_thresh})")
            
            template_path = self.config["red_template_path" if mode == "NORMAL" else "grey_template_path"]
            template_match = False
            max_val = 0.0
            
            if Path(template_path).exists():
                template = cv2.imread(str(template_path), cv2.IMREAD_GRAYSCALE)
                if template is not None:
                    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    result = cv2.matchTemplate(image_gray, template, cv2.TM_CCOEFF_NORMED)
                    _, max_val, _, _ = cv2.minMaxLoc(result)
                    template_thresh = self.config.get("template_confidence", 0.9)
                    logger.info(f"[DETECCION] Template match: {max_val:.3f} (threshold: {template_thresh})")
                    template_match = max_val >= template_thresh
            else:
                logger.warning(f"[DETECCION] Template no encontrado: {template_path}")
            
            if color_ratio > color_thresh or template_match:
                logger.info(f"[DETECCION] RESULTADO: Detectado ({'COLOR' if color_ratio > color_thresh else 'TEMPLATE'})")
                return True
            logger.info(f"[DETECCION] RESULTADO: No detectado")
            return False
            
        except Exception as e:
            logger.error(f"Error en deteccion: {e}")
            return None

    def check_availability(self):
        logger.info("[CHECK] Iniciando verificacion...")
        if self.config.get("verificacion_hubstaff", "ENABLED") == "ENABLED":
            is_active = self.get_hubstaff_window_state()
            if is_active:
                logger.info("Hubstaff detectado activo - Deteniendo monitor")
                return "STOP"
        else:
            logger.debug("Verificacion Hubstaff deshabilitada - Continuando monitoreo")
        
        image = self.capture_region()
        if image is None:
            logger.warning(f"Fallo captura ({self.cycle_count}/{self.detection_threshold})")
            self.save_debug_screenshot("capture_fail")
            return None
        
        logger.debug(f"Captura exitosa - imagen shape: {image.shape}")
        blocked = self.detect_budget_blocked(image)
        
        logger.debug(f"Deteccion result: {blocked}")
        mode = self.detection_mode
        
        if mode == "INVERSE":
            if blocked is True:
                if self.cycle_count > 0:
                    logger.info(f"Ciclo {self.cycle_count}/{self.detection_threshold}: Gris detectado. Contador REINICIADO.")
                self.cycle_count = 0
                logger.debug("Gris presente - Esperando que desaparezca")
            elif blocked is False:
                self.cycle_count += 1
                logger.info(f"[INVERSE] Ciclo {self.cycle_count}/{self.detection_threshold}: Gris NO detectado. Esperando confirmacion...")
                self.save_debug_screenshot(f"attempt_{self.cycle_count}")
                if self.cycle_count >= self.detection_threshold:
                    return "AVAILABLE"
            else:
                logger.warning(f"Deteccion inconclusive ({self.cycle_count}/{self.detection_threshold})")
                self.save_debug_screenshot("inconclusive")
        else:
            if blocked is True:
                if self.cycle_count > 0:
                    logger.info(f"Ciclo {self.cycle_count}/{self.detection_threshold}: Rojo detectado. Contador REINICIADO.")
                self.cycle_count = 0
                logger.debug("Budget bloqueado detectado - OK")
                return "BLOCKED"
            elif blocked is False:
                self.cycle_count += 1
                logger.info(f"[INFO] Ciclo {self.cycle_count}/{self.detection_threshold}: Rojo no detectado. Esperando confirmación...")
                self.save_debug_screenshot(f"attempt_{self.cycle_count}")
                
                if self.cycle_count >= self.detection_threshold:
                    return "AVAILABLE"
                return None
            else:
                logger.warning(f"Deteccion inconclusive ({self.cycle_count}/{self.detection_threshold})")
                self.save_debug_screenshot("inconclusive")
                return None
        
        return None

    def run(self):
        logger.info("=== SENTINEL v1.3 INICIADO ===")
        logger.info(f"Modo: {self.detection_mode} (NORMAL=Rojo, INVERSE=Gris)")
        logger.info(f"Intervalo: {self.config['check_interval_min']}-{self.config['check_interval_max']}s")
        logger.info(f"Region: ({self.config['calibration_x']}, {self.config['calibration_y']}) - {self.config['calibration_w']}x{self.config['calibration_h']}")
        logger.info(f"Confidence: 0.9 | Grayscale: True | Validacion: 3 ciclos (reset si reaparece)")
        
        while self.running:
            try:
                status = self.check_availability()
                
                if status == "STOP":
                    logger.info("Hubstaff activo - Apagando Sentinel")
                    break
                    
                elif status == "AVAILABLE":
                    logger.info(">>> 🚨 PRESUPUESTO DISPONIBLE DETECTADO (3/3) 🚨 <<<")
                    self.alert_manager.send_all_alerts("🚨 PRESUPUESTO DETECTADO 🚨 - Sentinel v1.3", self.last_debug_path)
                    time.sleep(300)
                    self.cycle_count = 0
                    
                interval = random.uniform(
                    self.config["check_interval_min"],
                    self.config["check_interval_max"]
                )
                time.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("Interrupcion manual")
                break
            except Exception as e:
                logger.error(f"Error en ciclo: {e}")
                time.sleep(60)
        
        logger.info("Sentinel terminado")

    def run_monitor_mode(self):
        logger.info("=== SENTINEL v1.3 MODO MONITOR ===")
        logger.info(f"Modo: {self.detection_mode} (NORMAL=Rojo, INVERSE=Gris)")
        logger.info(f"Intervalo: 10s (fijo para debug)")
        logger.info(f"Region: ({self.config['calibration_x']}, {self.config['calibration_y']}) - {self.config['calibration_w']}x{self.config['calibration_h']}")
        logger.info(f"Screenshots en cada ciclo: ACTIVADOS")
        logger.info("Presiona Ctrl+C para detener")
        
        while self.running:
            try:
                image = self.capture_region()
                if image is None:
                    logger.warning("Fallo captura")
                    time.sleep(10)
                    continue
                
                blocked = self.detect_budget_blocked(image)
                
                status = self.check_availability()
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                debug_file = self.save_debug_screenshot(f"monitor_{timestamp}")
                
                if status == "AVAILABLE":
                    logger.info(">>> 🚨 DISPONIBILIDAD DETECTADA 🚨 <<<")
                    time.sleep(300)
                    self.cycle_count = 0
                
                time.sleep(10)
                
            except KeyboardInterrupt:
                logger.info("Interrupcion manual")
                break
            except Exception as e:
                logger.error(f"Error en ciclo: {e}")
                time.sleep(10)
        
        logger.info("Monitor terminado")

def main():
    parser = argparse.ArgumentParser(description="Sentinel v1.3 - Monitor de Presupuesto")
    parser.add_argument("--test", action="store_true", help="Modo simulador de notificacion v1.3")
    parser.add_argument("--calibrate", action="store_true", help="Modo calibracion visual")
    parser.add_argument("--monitor", action="store_true", help="Modo monitoreo con screenshots en cada ciclo")
    args = parser.parse_args()
    
    if args.calibrate:
        run_visual_calibration()
    elif args.test:
        alert_manager = AlertManager()
        alert_manager.test_mode()
    elif args.monitor:
        sentinel = SentinelMonitor()
        sentinel.run_monitor_mode()
    else:
        sentinel = SentinelMonitor()
        sentinel.run()

if __name__ == "__main__":
    main()