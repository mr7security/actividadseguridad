# Actividad Seguridad IT — dashboard de proyectos e incidentes

Panel web del área de Seguridad de la Información: proyectos en ejecución (estado, avance, fechas, presupuesto aprobado, recursos) e incidentes resueltos en el año, por mes y por tipo.

- **Consulta**: cualquiera con acceso a la URL ve el dashboard en solo lectura.
- **Edición**: solo tras entrar con la contraseña (`/login`). Aparece el botón **Administrar** con pestañas Proyectos / Incidentes / Ajustes.
- **Datos**: SQLite `actividad.db` junto a la app. La primera vez que arranca se carga `seed.json`.
- **Copia de seguridad**: `/api/export` descarga todo en JSON (requiere sesión).

## Instalación en el servidor

```bash
cd ~ && git clone <repo> actividad-it && cd actividad-it
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env && nano .env        # APP_PASSWORD y APP_SECRET
sudo cp systemd/actividad-it.service /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now actividad-it
```

Abre `http://<servidor>:8090`. Actualizaciones: `git pull && sudo systemctl restart actividad-it`.

## Ficheros
- `app.py` — Flask: página, login, API REST (`/api/data`, `/api/proyectos/<id>`, `/api/incidentes/<id>`, `/api/caus/import` (CSV de ServiceDesk), `/api/config`, `/api/export`).
- `templates/index.html` — el dashboard (HTML/CSS/JS, sin dependencias externas salvo fuentes de Google).
- `seed.json` — datos iniciales (solo se usan si la base está vacía).
