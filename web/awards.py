from nicegui import ui, app
from data import crud
from web.side_menu import create_side_menu
import pandas as pd


def create_table(data, columns, threshold):
    df = pd.DataFrame(data, columns=columns)
    if len(columns) == 3:
        # Create pivot table
        matrix_df = df.pivot(
            columns=columns[1], index=columns[0], values=columns[2]
        )
        matrix_df = matrix_df.fillna(0)  # Fill NaN with 0

        # Reset index and rename first column
        matrix_df.reset_index(inplace=True)
        matrix_df = matrix_df.rename(columns={matrix_df.columns[0]: ""})

        # Prepare the columns for ui.table
        ui_columns = [{"name": col, "label": col, "field": col} for col in matrix_df.columns]

        # Prepare the rows data
        rows = []
        for _, row in matrix_df.iterrows():
            row_data = row.to_dict()  # Convert each row to a dictionary
            rows.append(row_data)

        # Generate UI table
        table = ui.table(columns=ui_columns, rows=rows)

        column_names = matrix_df.columns.tolist()
        
        # Add custom slot for styling values based on the threshold
        for col in column_names:
            if col != "":
                table.add_slot(f'body-cell-{col}', '''
                    <q-td key="count" :props="props">
                        <q-badge :color="props.value > ''' + str(threshold) +''' ? 'green' : 'grey'">
                            {{ props.value }}
                        </q-badge>
                    </q-td>
                ''')
        
        return table

    else:
        # Default table creation for non-pivot data
        ui_columns = [{"name": col, "label": col, "field": col} for col in df.columns]

        # Prepare the rows data
        rows = []
        for _, row in df.iterrows():
            row_data = row.to_dict()  # Convert each row to a dictionary
            rows.append(row_data)

        table = ui.table(columns=ui_columns, rows=rows)
        
        # Add custom slot for styling values based on the threshold
        table.add_slot('body-cell-Count', '''
            <q-td key="count" :props="props">
                <q-badge :color="props.value > ''' + str(threshold) +''' ? 'green' : 'grey'">
                    {{ props.value }}
                </q-badge>
            </q-td>
        ''')

        return table


# Create the awards page with a side menu
@ui.page("/awards")
async def page_awards():
    create_side_menu(selected_page="awards")

    # Retrieve the user's data from the application storage
    user = app.storage.user

    # Display the awards page
    ui.markdown("## Awards").classes("text-center")
    ui.markdown("Below is the list of awards you have earned:").classes("mb-2")

    awards_container = ui.column().classes("mt-4")  # Container to hold awards

    # Variable to store the selected countries - initialize as an empty list
    selected_countries = []
    def add_country(e):
        nonlocal selected_countries
        selected_countries = []
        for country in e.value:
            if country not in selected_countries:
                country = f"{country}"
                country = country.replace("'", '')
                country = country.replace("(", '')
                country = country.replace(")", '')
                country = country.replace(",", '')
                selected_countries.append(country)

    @ui.refreshable
    async def advanced_award_query():
        async def country_award_query():
            # add searchable dropdown for country which will be used to filter the award
            countrys = await crud.get_country_list(user["id"])
            country_award_query = ui.select(
                label="Country",
                options=countrys,
                multiple=True,
                on_change=add_country,
            ).classes("w-full")
            return country_award_query

        if "COUNTRY" in new_award_query.value:
            return await country_award_query()

    # Reactive variables to store input values
    new_award_name = ui.input("Award Name").classes("w-full")
    new_award_filter = ui.select(label="Filter", options=["DXCC"]).classes("w-full")
    new_award_query = ui.select(
        label="Query",
        options=["MODE", "BAND", "COUNTRY"],
        multiple=True,
        on_change=advanced_award_query.refresh,
    ).classes("w-full")
    await advanced_award_query()
    new_award_count = ui.number("Count", min=1).classes("w-full")


    # Function to create a new award
    async def create_award():
        if not new_award_name.value:
            ui.notify("Award Name is required!", color="negative")
            return
        if not new_award_count.value:
            ui.notify("Count is required!", color="negative")
            return

        # Retrieve values from UI components
        award_query_value = new_award_query.value
        award_filter_value = new_award_filter.value

        # Ensure the query list is transformed into a string
        if not award_query_value:
            award_query_value = ""
        else:
            award_query_value = ", ".join(award_query_value)

        # Access selected countries - add this
        print("Selected Countries:", selected_countries)

        query_text = None
        country_query = None

        # Add selected countries to the query string if applicable
        if "COUNTRY" in award_query_value and selected_countries:
            # write a sql query to filter the selected countries
            if len(selected_countries) == 1:
                country_query = f"COUNTRY = '{selected_countries[0]}'"
            else:
                country_query = f"COUNTRY IN {tuple(selected_countries)}"
            if query_text:
                query_text += f" AND {country_query}"
            else:
                query_text = f"{country_query}"
        # Save the new award using the CRUD method
        await crud.save_award(
            user_id=user["id"],
            name=new_award_name.value,
            query=award_query_value,
            count=new_award_count.value,
            filter=award_filter_value,
            query_text=country_query,
        )
        ui.notify("Award created successfully!", color="positive")
        await refresh_awards()  # Refresh the award list
        award_dialog.close()

    # Function to delete an award
    async def delete_award(award_id):
        await crud.delete_award(award_id)
        await refresh_awards()

    # Function to refresh the list of awards
    async def refresh_awards():
        awards_container.clear()  # Clear current awards list
        all_awards = await crud.load_awards(user_id=user["id"])
        if all_awards:
            for award in all_awards:
                (
                    found_connections,
                    columns,
                ) = await crud.get_award_query_results(
                    user_id=user["id"], query=award[3], filter_query=award[4]
                )
                with awards_container:
                    with ui.card().classes("w-full"):
                        ui.markdown(f"### {award[2]}").classes("mb-1")
                        ui.markdown(f"Query: {award[3]}").classes("mb-1")
                        ui.markdown(f"Query Text: {award[4]}").classes("mb-1")
                        ui.markdown(f"Filter: {award[6]}").classes("mb-1")
                        ui.markdown(f"Count: {award[5]}").classes("mb-1")
                        if columns != None:
                            columns.append("Count")
                        else:
                            columns = ["Count"]
                        create_table(found_connections, columns, award[5])
                        ui.button(
                            "Delete",
                            on_click=lambda award_id=award[0]: delete_award(award_id),
                        ).props("outlined")
        else:
            ui.markdown("No awards found.").classes("mt-2")

    # Dialog for creating a new award
    award_dialog = ui.dialog()
    with award_dialog:
        with ui.card():
            ui.markdown("### Create New Award")
            new_award_name.classes("w-full")  # Place input fields in dialog
            new_award_query.classes("w-full")
            with ui.row():
                ui.button("Cancel", on_click=award_dialog.close).props("flat").classes(
                    "mt-2"
                )
                ui.button("Create", on_click=create_award).props("unelevated").classes(
                    "mt-2"
                )

    await refresh_awards()

    # Button to open the create award dialog
    ui.button("Create New Award", on_click=award_dialog.open).props("outlined").classes(
        "mt-4"
    )