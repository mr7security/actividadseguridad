#!/usr/bin/env python3
"""Alta del incidente del 04/11/2026: detección Trend Micro en INFO68 (intelliphp.ls.exe). Idempotente."""
import subprocess, sys
from pathlib import Path
BASE = Path(__file__).resolve().parent
subprocess.run([sys.executable, str(BASE / "agregar_incidente.py"),
    "--id", "i-20261104-info68", "--fecha", "2026-11-04", "--tipo", "Malware", "--sev", "Baja", "--estado", "Abierto",
    "--ref", "Trend Micro · INFO68",
    "--titulo", "Detección Troj.Win32.TRX.XXPE50F13035 en INFO68 (intelliphp.ls.exe) — probable falso positivo",
    "--desc", "Equipo INFO68 (10.50.69.68), usuario dgabriel. Predictive Machine Learning de Trend Micro puso en cuarentena intelliphp.ls.exe (language server de IntelliPHP / PHP Tools, DEVSENSE) lanzado por vsixinstaller.exe de Visual Studio. Sin objetos destacados ni movimiento lateral. Pendiente: hash en VirusTotal, firma Authenticode de DEVSENSE, confirmación del usuario; si cuadra, restaurar, excluir por hash y reportar FP a Trend.",
    "--mitre", "T1204.002"], check=True)
