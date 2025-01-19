from nicegui import ui, app
from data import crud
from web.side_menu import create_side_menu
import pandas as pd

def create_table(data, columns):
    df = pd.DataFrame(data, columns=columns)
    ui.table.from_pandas(df).props('flat bordered')
    

# Create the awards page with a side menu
@ui.page('/awards')
async def page_awards():
    create_side_menu(selected_page='awards')

    # Retrieve the user's data from the application storage
    user = app.storage.user

    # Reactive variables to store input values
    new_award_name = ui.input('Award Name').classes('w-full')
    new_award_query = ui.input('Query').classes('w-full')

    # Function to create a new award
    async def create_award():
        if not new_award_name.value or not new_award_query.value:
            ui.notify('Both Award Name and Query are required!', color='negative')
            return
        await crud.save_award(user_id=user['id'], name=new_award_name.value, query=new_award_query.value)
        ui.notify('Award created successfully!', color='positive')
        await refresh_awards()  # Refresh the award list
        award_dialog.close()

    # Function to delete an award
    async def delete_award(award_id):
        await crud.delete_award(award_id)
        await refresh_awards()

    # Function to refresh the list of awards
    async def refresh_awards():
        awards_container.clear()  # Clear current awards list
        all_awards = await crud.load_awards(user_id=user['id'])
        if all_awards:
            for award in all_awards:
                found_connections, columns = await crud.get_award_query_results(user_id=user['id'], query=award[3])
                with awards_container:
                    with ui.card().classes('w-full'):
                        ui.markdown(f"### {award[2]}").classes('mb-2')
                        ui.markdown(award[3]).classes('mb-2')
                        columns.append('Count')
                        create_table(found_connections, columns)
                        ui.button('Delete', on_click=lambda award_id=award[0]: delete_award(award_id)).props('outlined')
        else:
            ui.markdown("No awards found.").classes('mt-2')

    # Dialog for creating a new award
    award_dialog = ui.dialog()
    with award_dialog:
        with ui.card():
            ui.markdown("### Create New Award")
            new_award_name.classes('w-full')  # Place input fields in dialog
            new_award_query.classes('w-full')
            with ui.row():
                ui.button('Cancel', on_click=award_dialog.close).props('flat').classes('mt-2')
                ui.button('Create', on_click=create_award).props('unelevated').classes('mt-2')

    # Display the awards page
    ui.markdown("## Awards").classes('text-center')
    ui.markdown("Below is the list of awards you have earned:").classes('mb-4')

    awards_container = ui.column().classes('mt-4')  # Container to hold awards
    await refresh_awards()

    # Button to open the create award dialog
    ui.button('Create New Award', on_click=award_dialog.open).props('outlined').classes('mt-4')
