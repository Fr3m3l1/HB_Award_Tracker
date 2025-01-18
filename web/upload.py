from nicegui import ui, app
from data import crud
import pandas as pd
import adif_io

from web.side_menu import create_side_menu

@ui.page('/upload')
async def page_upload():
    create_side_menu(selected_page='upload') 

    user = app.storage.user
    if not user:
        ui.notify("Please log in to access the upload page.", color="negative")
        ui.navigate.to('/login')
        return

    async def upload_file(e):
        file_str = e.content.read().decode('ISO-8859-1')
        qsos, header = adif_io.read_from_string(file_str)
        try:
            # Turn string to DataFrame using pandas
            df = pd.DataFrame(qsos)
            # Basic validation: check if required columns exist
            required_columns = ["CALL", "BAND", "MODE", "CONT", "COUNTRY", "FREQ", "DISTANCE", "EMAIL", "EQSL_QSLRDATE", "EQSL_QSLSDATE", "LOTW_QSLRDATE", "LOTW_QSLSDATE", "QSLRDATE", "QSLSDATE", "GRIDSQUARE", "LAT", "LON", "ANT_AZ", "ANT_EL", "DXCC", "FORCE_INIT", "K_INDEX", "PFX", "QSO_COMPLETE", "QSO_RANDOM", "RST_RCVD", "RST_SENT", "RX_PWR", "SFI", "STATION_CALLSIGN", "SWL", "TX_PWR", "QSO_DATE", "TIME_ON", "TIME_OFF"]
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                ui.notify(f"Invalid CSV format. Missing columns: {', '.join(missing_columns)}", type="error")
                return
            
            # Remove any extra columns
            df = df[required_columns]

            # Save to database using crud.save_qsos
            await crud.save_qsos(user['id'], df)

            ui.notify(f"Successfully uploaded {len(df)} QSOs!", type="positive")
            ui.navigate.to('/data_view')
        except Exception as e:
            ui.notify(f"Error processing CSV: {e}", type="error")

    with ui.card().classes('max-w-lg mx-auto mt-20'):
        ui.label('Upload your QSO data as a CSV file').classes('text-lg mb-4')
        ui.upload(on_upload=upload_file, multiple=False).props('accept=".ADI"')