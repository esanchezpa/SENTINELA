import os
import sys
import ctypes
import subprocess
from pathlib import Path

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
from config import CONFIG, create_default_env, load_config

def ensure_env():
    if not Path(".env").exists():
        create_default_env()
        print("[+] Creado .env por defecto")

def get_screen_region():
    print("\n=== MODO CALIBRACION ===")
    print("Presiona ENTER para comenzar la seleccion de region...")
    input()
    print("[*] Selecciona el area donde aparece 'Multiple limits' o Budget Rojo")
    print("[*] Usa el mouse para dibujar un rectangulo y presiona ENTER")
    
    try:
        import pyautogui
        from datetime import datetime
        
        region = pyautogui.alert(
            text="Selecciona el area con el mouse,\nluego presiona OK",
            title="Calibracion Sentinel",
            button="OK"
        )
        
        box = pyautogui.position()
        print(f"Posicion actual: {box}")
        
    except Exception as e:
        print(f"Error: {e}")
        box = None
    
    return box

def capture_template(x, y, w, h, output_path):
    try:
        screenshot = pyautogui.screenshot(region=(x, y, w, h))
        screenshot.save(output_path)
        print(f"[+] Template guardado: {output_path}")
        return True
    except Exception as e:
        print(f"[-] Error capturando: {e}")
        return False

def analyze_color(x, y, w, h):
    try:
        screenshot = pyautogui.screenshot(region=(x, y, w, h))
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        pixels = img.reshape(-1, 3)
        avg_color = pixels.mean(axis=0)
        
        hex_color = "#{:02X}{:02X}{:02X}".format(
            int(avg_color[2]), int(avg_color[1]), int(avg_color[0])
        )
        
        print(f"[+] Color promedio: {hex_color}")
        return hex_color
    except Exception as e:
        print(f"[-] Error analisis color: {e}")
        return None

def save_calibration(x, y, w, h, hex_color):
    env_path = Path(".env")
    lines = []
    
    if env_path.exists():
        with open(env_path, "r") as f:
            lines = f.readlines()
    
    new_lines = []
    found_x = found_y = found_w = found_h = found_hex = False
    
    for line in lines:
        if line.startswith("CALIBRATION_X="):
            new_lines.append(f"CALIBRATION_X={x}\n")
            found_x = True
        elif line.startswith("CALIBRATION_Y="):
            new_lines.append(f"CALIBRATION_Y={y}\n")
            found_y = True
        elif line.startswith("CALIBRATION_W="):
            new_lines.append(f"CALIBRATION_W={w}\n")
            found_w = True
        elif line.startswith("CALIBRATION_H="):
            new_lines.append(f"CALIBRATION_H={h}\n")
            found_h = True
        elif line.startswith("RED_COLOR_HEX="):
            new_lines.append(f"RED_COLOR_HEX={hex_color}\n")
            found_hex = True
        else:
            new_lines.append(line)
    
    if not found_x:
        new_lines.append(f"CALIBRATION_X={x}\n")
    if not found_y:
        new_lines.append(f"CALIBRATION_Y={y}\n")
    if not found_w:
        new_lines.append(f"CALIBRATION_W={w}\n")
    if not found_h:
        new_lines.append(f"CALIBRATION_H={h}\n")
    if not found_hex:
        new_lines.append(f"RED_COLOR_HEX={hex_color}\n")
    
    with open(env_path, "w") as f:
        f.writelines(new_lines)
    
    print("[+] Calibracion guardada en .env")

def main():
    ensure_env()
    print("=== SENTINEL CALIBRATION TOOL ===\n")
    
    try:
        region = get_screen_region()
        if region:
            x, y = region.x, region.y
            w, h = 200, 100
        else:
            x = int(input("Coordenada X: ") or "0")
            y = int(input("Coordenada Y: ") or "0")
            w = int(input("Ancho (W): ") or "200")
            h = int(input("Alto (H): ") or "100")
    except Exception:
        x, y, w, h = 0, 0, 200, 100
    
    print(f"\nRegion: x={x}, y={y}, w={w}, h={h}")
    
    template_dir = Path("templates")
    template_dir.mkdir(exist_ok=True)
    template_path = template_dir / "budget_red.png"
    
    if capture_template(x, y, w, h, str(template_path)):
        hex_color = analyze_color(x, y, w, h)
        if hex_color:
            save_calibration(x, y, w, h, hex_color)
    
    print("\n[✓] Calibracion completada")

if __name__ == "__main__":
    main()