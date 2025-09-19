# Iniciar el servidor (Windows / PowerShell)

Estos son los pasos mínimos para levantar el proyecto en tu máquina.

## 1) Abrir PowerShell en la carpeta del proyecto
- Ruta del proyecto: `C:\Users\eliza\OneDrive\Documentos\iscort`

## 2) Activar el entorno virtual (venv)

```powershell
# Desde la carpeta del proyecto
& C:\Users\eliza\OneDrive\Documentos\iscort\venv\Scripts\Activate.ps1
```

Si ves un error de ejecución de scripts, permite la ejecución para la sesión actual:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
& C:\Users\eliza\OneDrive\Documentos\iscort\venv\Scripts\Activate.ps1
```

## 3) Aplicar migraciones (solo si cambiaste modelos)

```powershell
C:\Users\eliza\OneDrive\Documentos\iscort\venv\Scripts\python.exe manage.py migrate
```

## 4) Iniciar el servidor de desarrollo

```powershell
C:\Users\eliza\OneDrive\Documentos\iscort\venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
```

- Abre en el navegador: http://127.0.0.1:8000/
- Para detenerlo: CTRL + C en la terminal.

## Notas útiles
- Crear superusuario (solo una vez):
```powershell
C:\Users\eliza\OneDrive\Documentos\iscort\venv\Scripts\python.exe manage.py createsuperuser
```
- Recolectar estáticos (si un día lo necesitas):
```powershell
C:\Users\eliza\OneDrive\Documentos\iscort\venv\Scripts\python.exe manage.py collectstatic
```
- Si instalas dependencias nuevas usa siempre el Python del venv.
