# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write(
    """Choose the Fruits you want in your smoothie!
    """
)

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be: ", name_on_order)

# Initialize Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch fruit options from the database
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME')).to_pandas()
fruit_names = my_dataframe['FRUIT_NAME'].tolist()

# Multiselect widget for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_names,
    max_selections=5
)

# Initialize `ingredients_string`
ingredients_string = ''

if ingredients_list:
    # Construct the ingredients string from the selected fruits
    ingredients_string = ' '.join(ingredients_list)

    # Fetch nutrition information for each fruit
    for fruit_chosen in ingredients_list:
        st.subheader(f"{fruit_chosen} Nutrition Information")
        try:
            smoothiefroot_response = requests.get(
                f"https://my.smoothiefroot.com/api/fruit/all/{fruit_chosen}"
            )
            if smoothiefroot_response.status_code == 200:
                st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
            else:
                st.error(f"Failed to fetch nutrition information for {fruit_chosen}.")
        except Exception as e:
            st.error(f"An error occurred while fetching data for {fruit_chosen}: {e}")

# Construct the SQL insert statement
my_insert_stmt = f"""
INSERT INTO smoothies.public.orders(ingredients, name_on_order)
VALUES ('{ingredients_string}', '{name_on_order}');
"""

# Button to submit the order
time_to_insert = st.button('Submit Order')

if time_to_insert:
    if ingredients_string and name_on_order:
        # Execute the SQL insert statement
        try:
            session.sql(my_insert_stmt).collect()
            st.success('Your Smoothie is ordered!', icon="✅")
        except Exception as e:
            st.error(f"An error occurred while placing the order: {e}")
    else:
        st.warning("Please select ingredients and provide a name for the smoothie.")
