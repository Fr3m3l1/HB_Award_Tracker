from nicegui import ui, app

@ui.page('/')
def page_home():
    # Check if the user is logged in
    user = app.storage.user
    if user:
        # Display a welcome message and links to other pages
        ui.markdown(f"Welcome, {user['username']}!")
        ui.link('Upload CSV', '/upload')
        ui.link('View Data', '/data_view')
    else:
        # Redirect to the login page if the user is not logged in
        ui.navigate.to('/login')