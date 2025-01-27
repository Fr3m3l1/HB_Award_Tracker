from nicegui import ui, app
from data import crud, db_init
import logging as log
from dotenv import load_dotenv
import os
import hashlib
import time

# Import pages from the `ui` module
import web.home
import web.upload
import web.data_view
import web.awards
import web.settings

load_dotenv()

MIN_PASSWORD_LENGTH = 8

# Initialize the logger
if os.getenv('ENV') == 'development':
    log.basicConfig(level=log.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
else:
    log.basicConfig(level=log.WARNING, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Initialize the database
db_init.init_db()
log.info('Database initialized')

async def login_user(username: str, password: str):
    # Rate limiting check


    try:
        # Client-side hashing
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        user = await crud.authenticate_user(username, hashed_password)
        
        if user:
            # Successful login
            app.storage.user.update({
                'id': user[0],
                'username': user[1],
                'failed_attempts': 0,
                'last_failed_attempt': 0
            })
            ui.notify(f'Welcome back, {user[1]}!', color='positive')
            ui.navigate.to('/')
        else:
            # Failed login

            message = f'Invalid credentials.' 
            ui.notify(message, color='negative')
            
    except Exception as e:
        log.error(f'Login error: {str(e)}')
        ui.notify('An error occurred during login. Please try again.', color='negative')

@ui.page('/login')
def login_page():
    if app.storage.user.get('id'):
        ui.navigate.to('/')
        return

    with ui.column().classes('absolute-center items-center w-full p-4'):
        with ui.card().classes('max-w-md w-full shadow-xl rounded-lg'):
            # Header Section
            with ui.column(align_items="center").classes('items-center gap-4 mb-8'):
                ui.icon('security', size='xl', color='primary').classes('text-4xl')
                ui.label('HAM Radio Dashboard').classes('text-2xl font-bold text-primary')
                ui.label('Please sign in to continue').classes('text-gray-600')

            # Login Form
            with ui.column().classes('w-full gap-4'):
                username = ui.input(label='Username', validation={
                    'Please enter a username': lambda value: bool(value.strip())
                }).props('outlined clearable').classes('w-full')
                
                password = ui.input(
                    label='Password',
                    password=True,
                    password_toggle_button=True,
                    validation={
                        f'Password must be at least {MIN_PASSWORD_LENGTH} characters': lambda v: len(v) >= MIN_PASSWORD_LENGTH
                    }
                ).props('outlined').classes('w-full')

                #remember_me = ui.checkbox('Remember me').props('dense')
                
                ui.button('Sign In', on_click=lambda: login_user(username.value, password.value)) \
                    .props('unelevated color=primary').classes('w-full')

            # Footer Links
            #with ui.column().classes('items-center mt-6 gap-3'):
            #    ui.link('Forgot Password?', '/password-reset').classes('text-sm text-gray-600 hover:text-primary')
            #    ui.separator().props('inset')
            #    ui.label('New user?').classes('text-gray-600')
            #    ui.button('Create Account', on_click=lambda: ui.navigate.to('/register')) \
            #        .props('outline color=primary').classes('w-full')


@ui.page('/logout')
def logout_page():
    app.storage.user.clear()
    ui.notify('You have been logged out.', color='positive')
    ui.navigate.to('/login')

# Start the NiceGUI app
ui.run(storage_secret="my-secret-key", title="HAM Dashboard", port=8090)