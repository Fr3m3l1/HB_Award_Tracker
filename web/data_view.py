from nicegui import ui, app
from data import crud
from typing import Dict

from web.side_menu import create_side_menu

@ui.page('/data_view')
async def page_data_view():
    create_side_menu(selected_page='data_view')

    # Retrieve the user's QSO data from the database
    user = app.storage.user
    if user:
        qsos = await crud.get_qsos(user_id=user['id'])  

        # Drop the user_id column
        qsos = qsos.drop(columns=['user_id', 'id'])

        # Convert DataFrame columns (Index) to a list
        qsos_dict = qsos.to_dict('records')
        qsos_columns = qsos.columns.tolist()  # Convert to list

        columns = []

        for column in qsos_columns:
            columns.append({'name': column, 'label': column, 'field': column, 'required': True, 'align': 'left'})

        # Store column visibility state
        visibility_state = {column['field']: True for column in columns}

        def toggle(column: Dict, visible: bool) -> None:
            visibility_state[column['field']] = visible
            qso_table.update()  # Update table to reflect changes

        # Show the row count
        ui.label(f"Total QSOs: {len(qsos)}")

        with ui.button(icon='menu'):
            with ui.menu(), ui.column().classes('gap-0 p-2'):
                for column in columns:
                    if column['field'] not in ['EMAIL', 'ANT_AZ', 'ANT_EL', 'DXCC', 'FORCE_INIT', 'K_INDEX', 'QSO_RANDOM', 'RX_PWR', 'SFI', 'TX_PWR', 'LAT', 'LON']:
                        ui.switch(column['label'], value=True, on_change=lambda e, column=column: toggle(column, e.value))
                    else:
                        ui.switch(column['field'], value=False, on_change=lambda e, column=column: toggle(column, e.value))

        with ui.card():
            if qsos_dict:
                qso_table = ui.table(columns=columns, rows=qsos_dict)
                # Set initial visibility of columns based on `visibility_state`
                for column in columns:
                    if not visibility_state[column['field']]:
                        column['classes'] = 'hidden'
                        column['headerClasses'] = 'hidden'
            else:
                ui.label('No data to display.')
    else:
        ui.label('Please log in to view your data.')
        ui.link('Login', '/login')