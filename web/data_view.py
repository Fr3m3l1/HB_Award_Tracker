from nicegui import ui, app
from data import crud

from web.side_menu import create_side_menu

@ui.page('/data_view')
async def page_data_view():
    create_side_menu(selected_page='data_view')

    # Retrieve the user's QSO data from the database
    user = app.storage.user
    if user:
        # Initial page size and starting point for data
        page_size = 10
        current_page = 0
        all_qsos_loaded = False
        loaded_qsos = []

        # Drop columns you don't need initially
        drop_columns = ['user_id', 'id']
        hidden_columns = ['EMAIL', 'ANT_AZ', 'ANT_EL', 'DXCC', 'FORCE_INIT', 
                          'K_INDEX', 'QSO_RANDOM', 'RX_PWR', 'SFI', 
                          'TX_PWR', 'LAT', 'LON']

        async def fetch_qsos(page: int):
            """Fetch a specific page of QSOs."""
            nonlocal all_qsos_loaded
            offset = page * page_size
            qsos = await crud.get_qsos(user_id=user['id'], offset=offset, limit=page_size)
            
            if len(qsos) < page_size:
                all_qsos_loaded = True
            
            # Drop unwanted columns and convert to dictionary
            qsos = qsos.drop(columns=drop_columns)
            return qsos.to_dict('records')

        async def load_more_data():
            """Load more data and refresh the table."""
            nonlocal current_page, loaded_qsos
            new_qsos = await fetch_qsos(current_page)
            loaded_qsos.extend(new_qsos)
            current_page += 1
            data_view.refresh()
            show_loaded_count.refresh()

        # Fetch the first page of QSOs
        loaded_qsos = await fetch_qsos(current_page)
        current_page += 1

        # Set up table columns
        qsos_columns = loaded_qsos[0].keys() if loaded_qsos else []
        visibility_state = {col: col not in hidden_columns for col in qsos_columns}
        columns = [{'name': col, 'label': col, 'field': col, 'required': True, 'align': 'left'}
                   for col in qsos_columns]

        def toggle(column_field: str, visible: bool) -> None:
            visibility_state[column_field] = visible
            data_view.refresh()

        # Show the row count
        @ui.refreshable
        async def show_loaded_count():
            total_qsos = await crud.get_qsos(user_id=user['id'])
            ui.label(f"Loaded QSOs: {len(loaded_qsos)}/{len(total_qsos)}")

        with ui.button(icon='menu'):
            with ui.menu(), ui.column().classes('gap-0 p-2'):
                for column in columns:
                    initial_value = visibility_state[column['field']]
                    ui.switch(
                        column['label'],
                        value=initial_value,
                        on_change=lambda e, column_field=column['field']: toggle(column_field, e.value)
                    )

        @ui.refreshable
        def data_view():
            with ui.card():
                if loaded_qsos:
                    qso_table = ui.table(columns=columns, rows=loaded_qsos)

                    # Adjust column visibility dynamically
                    for column in columns:
                        if not visibility_state[column['field']]:
                            column['classes'] = 'hidden'
                            column['headerClasses'] = 'hidden'
                        else:
                            column['classes'] = ''
                            column['headerClasses'] = ''
                else:
                    ui.label('No data to display.')

        await show_loaded_count()
        data_view()

        # Add a "Load More" button if there are more rows to fetch
        async def handle_load_more_click():
            if not all_qsos_loaded:
                await load_more_data()
            else:
                ui.notify('All QSOs are loaded.')

        with ui.row():
            load_more_button = ui.button('Load More', on_click=handle_load_more_click)

    else:
        ui.label('Please log in to view your data.')
        ui.link('Login', '/login')
