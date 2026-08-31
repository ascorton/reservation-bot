# reservation-bot

Bot que automatiza la reserva de clases en un box de CrossFit gestionado a través de la plataforma **CrossHero**.

## Qué hace

CrossHero abre cada clase a reserva exactamente **25 horas antes de su hora de inicio**. El bot se queda corriendo en segundo plano y, en el instante en que se abre la ventana de reserva de una clase concreta, hace login automático y reserva plaza sin intervención manual.

## Cómo funciona

1. **`main.py`** programa, con la librería [`schedule`](https://pypi.org/project/schedule/), una lista de disparos (día de la semana + hora) que coinciden con el momento exacto en que se abre cada clase (25h antes de su inicio). Se queda en un bucle infinito comprobando cada 60 segundos si toca ejecutar alguno.
El **`main.py`** no será necesario en el momento en que se ejecute desde Home Assistant dado que las llamadas a la función de reserva se hace desde HA.

2. Cuando llega uno de esos instantes, se ejecuta **`run_booking_script()`** (`booking.py`), que:
   - Inicia sesión en CrossHero (`perform_login`), reutilizando el token de autenticidad (CSRF) que exige el sitio.
   - Llama a **`get_class_id()`** (`classes_management.py`) para averiguar el ID de la clase que se acaba de abrir: calcula `ahora + 25h` para saber la fecha y hora exactas de esa clase, construye la URL del calendario filtrada por esa fecha y por el programa indicado (`OPEN WOD` por defecto), y busca en el HTML la opción cuyo texto coincide con esa hora.
   - Llama a **`book_class()`** para enviar la reserva (`POST`) de esa clase concreta.

3. **`config.py`** carga las credenciales y URLs desde un archivo `.env`, y expone además:
   - `PROGRAM_IDS`: diccionario que traduce el nombre de cada programa/clase (tal como aparece en la web) a su ID interno de CrossHero.
   - `PUBLICATION_LEAD_TIME`: horas de antelación con las que se abre cada clase (25).

## Horario programado (`main.py`)

| Se ejecuta | Reserva la clase de | Motivo |
|---|---|---|
| Domingo 16:00 y 17:00 | Lunes 17:00 y 18:00 | cada clase abre 25h antes |
| Lunes 16:00 y 17:00 | Martes 17:00 y 18:00 | ídem |
| Martes 16:00 y 17:00 | Miércoles 17:00 y 18:00 | ídem |
| Jueves 16:00 y 17:00 | Viernes 17:00 y 18:00 | ídem |
| Viernes 09:00 | Sábado 10:00 | única clase del sábado |

No hay disparos los miércoles ni los sábados porque el box no tiene clase los jueves ni los domingos.

## Estructura del proyecto

| Archivo | Contenido |
|---|---|
| `main.py` | Programa el horario (`schedule`) y mantiene el bot corriendo indefinidamente |
| `booking.py` | Orquesta el flujo completo: login → búsqueda de clase → reserva |
| `classes_management.py` | Lógica de búsqueda del ID de clase (`get_class_id`) y envío de la reserva (`book_class`) |
| `config.py` | Carga `.env`, URLs fijas del sitio, `PROGRAM_IDS` y `PUBLICATION_LEAD_TIME` |
| `.env.example` | Plantilla de las variables de entorno necesarias |
| `requirements.txt` | Dependencias del proyecto y sus versiones exactas |

## Instalación

```
git clone <url-del-repo>
cd reservation-bot
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

Copia `.env.example` a `.env` y rellena tus credenciales reales:

```
BOX_USER=tu_correo_o_usuario
BOX_PASSWORD=tu_contraseña
BOX_API_URL=https://url-de-la-api-o-web-de-reservas.com
```

## Ejecución

```
python main.py
```

El proceso debe quedarse abierto (terminal o como servicio en segundo plano) para que el horario se dispare. Si el equipo se apaga, se suspende o pierde conexión durante una de las ventanas de reserva, esa reserva concreta no se hará.

## Reservar otro tipo de clase

Por defecto se reserva el programa `"OPEN WOD-"`. Para reservar otro, pásalo como argumento a `run_booking_script`:

```python
run_booking_script(program="YOGA")
```

Las claves válidas son las del diccionario `PROGRAM_IDS` en `config.py`. Si se pasa un nombre que no existe, `get_class_id` lanza un `ValueError` indicando las opciones válidas disponibles.

## Limitaciones conocidas

- `datetime.now()` usa la hora local del sistema donde corre el script, sin zona horaria explícita — si se despliega en un servidor con otro huso horario, los horarios se desajustarían.
- El bot no persiste estado entre ejecuciones: si el proceso se reinicia a mitad de una ventana de reserva, esa reserva no se reintenta automáticamente.
