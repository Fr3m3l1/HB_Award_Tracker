from nicegui import ui, app

def create_side_menu(selected_page=None):
    # Define CSS styles for the menu
    ui.add_css('''
        .menu-item {
            transition: all 0.3s ease;
            cursor: pointer;
        }
        .menu-item:hover {
            background-color: #1e3a8a !important;
            transform: translateX(4px);
        }
        .selected-menu-item {
            background-color: #1e3a8a !important;
            border-left: 4px solid #93c5fd !important;
        }
        .drawer-footer {
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
    ''')

    user = app.storage.user

    with ui.header().classes('row items-center p-4 bg-blue-800 shadow-lg') as header:
        ui.button(icon='menu', on_click=lambda: left_drawer.toggle()).props('flat color=white round') \
            .classes('lg:hidden')  # Hide on larger screens
        ui.label('HAM Dashboard').classes('text-white text-xl font-bold ml-4')

    with ui.left_drawer().classes('bg-blue-900 text-white w-64').props('bordered') as left_drawer:
        # Drawer Header
        with ui.column().classes('items-center p-4 mb-4'):
            ui.icon('account_circle', size='xl').classes('text-white')
            if user:
                ui.label(f'Welcome Back, {user["username"]}!').classes('text-white text-lg font-medium')
            else:
                ui.label('Welcome!').classes('text-white text-lg font-medium')

        # Navigation Menu
        menu_items = [
            {'page': 'home', 'label': 'Dashboard', 'icon': 'dashboard'},
            {'page': 'upload', 'label': 'Upload Data', 'icon': 'cloud_upload'},
            {'page': 'data_view', 'label': 'Data Analysis', 'icon': 'insights'},
            {'page': 'awards', 'label': 'Awards', 'icon': 'assignment'},
            {'page': 'settings', 'label': 'Settings', 'icon': 'settings'},
        ]

        for item in menu_items:
            with ui.link(target=f'/{item["page"]}').classes('w-full text-white no-underline menu-item').props('active-color=white'):
                with ui.row().classes(f'items-center p-3 space-x-4 {"selected-menu-item" if selected_page == item["page"] else ""}'):
                    ui.icon(item['icon']).classes('text-white')
                    ui.label(item['label']).classes('text-white')
        
        # Drawer Footer
        with ui.column().classes('drawer-footer mt-auto p-4'):
            with ui.row().classes('items-center space-x-2 menu-item').on('click', lambda: ui.navigate.to('logout')):
                ui.icon('logout').classes('text-white')
                ui.label('Log Out').classes('text-white')

    # Add responsive behavior
    ui.query('.q-drawer').classes('shadow-xl')
    ui.query('body').classes('transition-padding duration-300')
    
    # Toggle drawer on mobile when route changes
    def close_drawer():
        if left_drawer.value:
            left_drawer.toggle()