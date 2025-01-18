from nicegui import ui, app

# Define the side menu content
def create_side_menu(selected_page=None):
    with ui.header().classes(replace='row items-center p-4') as header:
        ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').props('flat color=white')

    with ui.left_drawer().classes('bg-blue-500 text-white w-64') as left_drawer:
        # Add a title or logo to the side menu
        ui.label('Navigation').classes('text-2xl font-semibold py-4 px-6')

        # Create styled menu items with icons and hover effects
        menu_items = [
            {'page': 'home', 'label': 'Home', 'icon': 'home'},
            {'page': 'upload', 'label': 'Upload', 'icon': 'cloud_upload'},
            {'page': 'data_view', 'label': 'Data View', 'icon': 'view_in_ar'},
            {'page': 'logout', 'label': 'Logout', 'icon': 'logout'},
        ]

        for item in menu_items:
            if selected_page == item['page']:
                # Apply a selected style to the active link
                ui.link(item['label'], f'/{item["page"]}').props('class=selected p-4 flex items-center text-white bg-blue-700 rounded-md')
            else:
                # Regular menu item style
                ui.link(item['label'], f'/{item["page"]}').props('class=p-4 flex items-center text-white hover:bg-blue-600 rounded-md')
