from nicegui import ui, app
from data import crud
import pandas as pd
import adif_io
from web.side_menu import create_side_menu

@ui.page('/upload')
def page_upload():
    create_side_menu(selected_page='upload')

    user = app.storage.user
    if not user:
        ui.notify("Please log in to access the upload page.", color="negative")
        ui.navigate.to('/login')
        return

    # Initialize state variables
    processing = False
    upload_progress = ui.linear_progress(value=0).props('instant-feedback').classes('w-full hidden')
    status_label = ui.label().classes('text-sm')

    async def upload_file(e):
        nonlocal processing
        try:
            processing = True
            upload_progress.classes(remove='hidden')
            status_label.set_text('Reading file...')
            
            file_str = e.content.read().decode('ISO-8859-1')
            qsos, header = adif_io.read_from_string(file_str)
            
            status_label.set_text('Processing data...')
            df = pd.DataFrame(qsos)
            
            # Validate required columns
            required_columns = ["CALL", "BAND", "MODE", "QSO_DATE", "TIME_ON"]
            possible_columns = ["CALL", "BAND", "MODE", "TIME_ON", "TIME_OFF", "FREQ", "COUNTRY", "DISTANCE", "EMAIL",
                    "EQSL_QSLRDATE", "EQSL_QSLSDATE", "LOTW_QSLRDATE", "LOTW_QSLSDATE", "QSLRDATE", "QSLSDATE", "GRIDSQUARE", "LAT", "LON",
                    "ANT_AZ", "ANT_EL", "CONT", "DXCC", "FORCE_INIT", "K_INDEX", "PFX", "QSO_COMPLETE", "QSO_RANDOM", "RST_RCVD", "RST_SENT",
                    "RX_PWR", "SFI", "STATION_CALLSIGN", "SWL", "TX_PWR", "QSO_DATE"]
            missing = [col for col in required_columns if col not in df.columns]
            if missing:
                raise ValueError(f"Missing required columns: {', '.join(missing)}")
            
            # Clean data
            df['BAND'] = df['BAND'].str.lower().str.strip()

            # Make sure that all the columns are available
            for col in possible_columns:
                if col not in df.columns:
                    df[col] = None
            
            status_label.set_text('Saving to database...')
            await crud.save_qsos(user['id'], df)
            
            ui.notify(f"Successfully uploaded {len(df)} QSOs!", type="positive")
            ui.navigate.to('/data_view')
            
        except Exception as e:
            ui.notify(f"Upload failed: {str(e)}", type="negative")
            status_label.set_text(f"Error: {str(e)}")
        finally:
            processing = False
            upload_progress.classes('hidden')
            status_label.set_text('')

    with ui.card().classes('max-w-lg mx-auto mt-20'):
        ui.label('Upload QSO Data (ADI Format)').classes('text-lg mb-4 font-bold')
        
        # Upload component with progress feedback
        upload = ui.upload(
            on_upload=upload_file, 
            multiple=False,
            auto_upload=True
        ).props('accept=".adi,.ADI" label="Select ADI file"')
        
        upload_progress
        status_label

        # Help text
        ui.markdown('''
            **Requirements:**
            - Valid ADI file format
            - Must include: CALL, BAND, MODE, QSO DATE, TIME ON
            - Max size: 10MB
        ''').classes('text-sm mt-4 text-gray-600')