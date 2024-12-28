import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Title and Description
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the Fruits you want in your smoothie!")

# Input for Smoothie Name
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be: ", name_on_order)

# Snowflake Connection
try:
    cnx = st.experimental_connection("snowflake")
    session = cnx.session()
    my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME')).collect()
    fruit_names = [row['FRUIT_NAME'] for row in my_dataframe]  # Convert to a list of strings
except Exception as e:
    st.error("Error connecting to Snowflake: " + str(e))
    st.stop()

# Multiselect for Ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_names,
    max_selections=5
)

if ingredients_list:
    # Display Nutrition Information
    for fruit_chosen in ingredients_list:
        st.subheader(f"{fruit_chosen} Nutrition Information")
        try:
            response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen}")
            if response.status_code == 200:
                st.dataframe(data=response.json(), use_container_width=True)
            else:
                st.warning(f"Could not fetch nutrition data for {fruit_chosen}.")
        except Exception as e:
            st.error(f"Error fetching data for {fruit_chosen}: {e}")

# Construct SQL Insert Statement
if name_on_order and ingredients_list:
    try:
        ingredients_string = ', '.join(ingredients_list)  # Create a comma-separated string of ingredients
        my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES (%s, %s)
        """
        time_to_insert = st.button('Submit Order')
        if time_to_insert:
            session.sql(my_insert_stmt, [ingredients_string, name_on_order]).collect()
            st.success('Your Smoothie is ordered!', icon="✅")
    except Exception as e:
        st.error(f"Error inserting order into database: {e}")
