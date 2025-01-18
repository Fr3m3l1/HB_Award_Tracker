from nicegui import ui, app

from web.side_menu import create_side_menu

@ui.page('/home')
def page_home():
    create_side_menu(selected_page='home')
    # Check if the user is logged in
    user = app.storage.user
    if user:
        # Display a welcome message and links to other pages
        ui.markdown(f"Welcome, {user['username']}!")
    else:
        # Redirect to the login page if the user is not logged in
        ui.navigate.to('/login')

@ui.page('/')
def page_root():
    ui.navigate.to('/home')