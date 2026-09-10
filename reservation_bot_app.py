import appdaemon.plugins.hass.hassapi as hass
from datetime import datetime, timedelta
from booking import run_booking_script
from config import PUBLICATION_LEAD_TIME

# (nombre_dia, abreviatura_appdaemon, indice_lunes=0...sabado=5)
DIAS = [
    ("lunes", "mon", 0),
    ("martes", "tue", 1),
    ("miercoles", "wed", 2),
    ("jueves", "thu", 3),
    ("viernes", "fri", 4),
    ("sabado", "sat", 5),
]

ABBR_POR_WEEKDAY = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

# 2024-01-01 es lunes; se usa solo como fecha de referencia para los calculos
_REF_MONDAY = datetime(2024, 1, 1)
# Nombre del servicio notify de la aplicacion movil de Home Assistant.
NOTIFICATION_SERVICE = "notify/mobile_app_pixel_10_pro"


class ReservationBot(hass.Hass):

    def initialize(self):
        self.handles = []

        # Escucha cambios en TODOS los input_select de tipo/hora, para
        # reprogramar los run_daily automaticamente cuando cambie algo
        entidades = []
        for dia, _, _ in DIAS:
            for slot in [1, 2]:
                entidades.append(f"input_select.reserva_{dia}_{slot}_tipo")
                entidades.append(f"input_select.reserva_{dia}_{slot}_hora")

        for entidad in entidades:
            self.listen_state(self.reprogramar, entidad)

        # Programa el horario inicial nada mas arrancar
        self.reprogramar(None, None, None, None, None)

    def reprogramar(self, entity, attribute, old, new, kwargs):
        # Se reconstruye toda la agenda para que los cambios de configuracion
        # sustituyan los horarios anteriores en lugar de duplicarlos.
        # Cancela todos los run_daily anteriores antes de crear los nuevos
        for h in self.handles:
            self.cancel_timer(h)
        self.handles = []
        reservas_programadas = []

        for dia, _, dia_idx in DIAS:
            for slot in [1, 2]:
                tipo = self.get_state(f"input_select.reserva_{dia}_{slot}_tipo")
                hora = self.get_state(f"input_select.reserva_{dia}_{slot}_hora")

                if not tipo or not hora or tipo == "Ninguna" or hora == "Ninguna" or hora.startswith("---"):
                    continue

                try:
                    hh, mm = map(int, hora.split(":"))
                except ValueError:
                    self.log(f"Hora '{hora}' invalida en {dia} clase {slot}, se omite.", level="WARNING")
                    continue

                # Calcula cuando hay que lanzar el intento: clase menos la
                # antelacion necesaria para que aparezca publicada.
                target_dt = _REF_MONDAY.replace(hour=hh, minute=mm) + timedelta(days=dia_idx)
                trigger_dt = target_dt - timedelta(hours=PUBLICATION_LEAD_TIME)
                trigger_day_abbr = ABBR_POR_WEEKDAY[trigger_dt.weekday()]
                trigger_time_str = trigger_dt.strftime("%H:%M:%S")

                handle = self.run_daily(
                    self.run_booking,
                    trigger_time_str,
                    constrain_days=trigger_day_abbr,
                    program=tipo,
                    dia=dia,
                    hora=hora,
                    slot=slot,
                )
                self.handles.append(handle)
                # Se conserva la hora de la clase para incluirla en el aviso
                # que recibira el movil cuando se ejecute la reserva.
                reservas_programadas.append(f"{dia.upper()} {hora} {tipo}")

                self.log(
                    f"{dia} clase {slot} ('{tipo}' @ {hora}) -> disparo {trigger_day_abbr} {trigger_time_str}"
                )

        # El tag fijo hace que Home Assistant actualice esta notificacion en
        # vez de crear una nueva cada vez que se reprograma.
        mensaje = "\n".join(reservas_programadas)
        if NOTIFICATION_SERVICE:
            self.call_service(
                NOTIFICATION_SERVICE,
                title="Reservation Bot",
                message=mensaje,
                data={"tag": "reservation_bot_reprogramacion"},
            )

    def run_booking(self, kwargs):
        # El callback recibe estos valores desde el run_daily programado.
        if self.get_state("input_boolean.enable_reservation_bot") != "on":
            self.log("Reservas desactivadas (interruptor maestro en off), no se ejecuta nada.")
            return

        program = kwargs.get("program")
        dia = kwargs.get("dia")
        hora = kwargs.get("hora")
        slot = kwargs.get("slot")

        self.log(f"{dia} clase {slot}: intentando reservar '{program}'...")
        try:
            # Si no se produce una excepcion, se informa de que el proceso
            # termino correctamente.
            run_booking_script(program)
            mensaje = f"RESERVA CORRECTA\n{dia.upper()} {hora} {program}"
            self.log(mensaje)

            if NOTIFICATION_SERVICE:
                self.call_service(
                    NOTIFICATION_SERVICE,
                    title="Reservation Bot",
                    message=mensaje,
                    # El resultado reutiliza su propia notificacion.
                    data={"tag": "reservation_bot_resultado"},
                )
        except Exception as e:
            mensaje = f"RESERVA FALLIDA\n{dia.upper()} {hora} {program}\n{e}"
            self.log(mensaje, level="ERROR")

            if NOTIFICATION_SERVICE:
                self.call_service(
                    NOTIFICATION_SERVICE,
                    title="Reservation Bot",
                    message=mensaje,
                    data={"tag": "reservation_bot_resultado"},
                )