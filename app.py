from nicegui import ui, app
from data import crud, db_init
import logging as log
from dotenv import load_dotenv
import os

# Import pages from the `ui` module
import web.home
import web.upload
import web.data_view
import web.awards

load_dotenv()

# Initialize the logger
if os.getenv('ENV') == 'development':
    log.basicConfig(level=log.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
else:
    log.basicConfig(level=log.WARNING, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Initialize the database
db_init.init_db()
log.info('Database initialized')

# Define the user login function
async def login_user(username, password):
    # Validate the username and password
    user = await crud.authenticate_user(username, password)
    if user:
        # Store user information in the session
        app.storage.user['id'] = user[0]
        app.storage.user['username'] = user[1]
        ui.notify(f'Welcome, {user[1]}!', color='positive')
        ui.navigate.to('/')
    else:
        ui.notify('Invalid username or password', color='negative')

# Create the login page
@ui.page('/login')
def login_page():
    with ui.card().classes('max-w-lg mx-auto mt-20'):
        ui.label('Please log in').classes('text-lg mb-4')
        username_input = ui.input(label='Username').props('outlined')
        password_input = ui.input(label='Password', password=True, password_toggle_button=True).props('outlined')
        ui.button('Login', on_click=lambda: login_user(
            username_input.value, password_input.value
        )).props('unelevated')

@ui.page('/logout')
def logout_page():
    app.storage.user.clear()
    ui.notify('You have been logged out.', color='positive')
    ui.navigate.to('/login')

# Start the NiceGUI app
ui.run(storage_secret="my-secret-key", title="HM Dashboard", port=8090)