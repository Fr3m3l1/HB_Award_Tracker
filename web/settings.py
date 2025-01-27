from nicegui import ui, app

from web.side_menu import create_side_menu

@ui.page('/settings')
def page_settings():
    create_side_menu(selected_page='settings')
    # Check if the user is logged in
    user = app.storage.user
    if user:
        # Display a welcome message and links to other pages
        ui.markdown(f"Welcome, {user['username']}!")

        ui.markdown('## DOES NOT WORK YET')

        # Create a form to update the user's settings
        with ui.card():
            ui.label('Settings')
            ui.input(label='Username', value=user['username'])
            ui.input(label='Password', password=True, password_toggle_button=True)
            ui.button('Save', on_click=lambda: ui.notify('Settings saved', color='positive')).props('unelevated')
    else:
        # Redirect to the login page if the user is not logged in
        ui.navigate.to('/login')