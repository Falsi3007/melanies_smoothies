# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write(
    """Choose the Fruits you want in your smoothie!
    """)

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be: ", name_on_order)

cnx =  st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))

# Convert the Snowflake table to a Pandas DataFrame
pd_pf = my_dataframe.to_pandas()

# Multiselect widget for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_pf['FRUIT_NAME'].tolist(),  # Convert FRUIT_NAME column to list
    max_selections=5
)

# Initialize `ingredients_string` to an empty string
ingredients_string = ''

if ingredients_list:
    # Construct the ingredients string and fetch `SEARCH_ON` values
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        st.show(pd_pf)
        search_on = pd_pf.loc[pd_pf['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write(f"The search value for {fruit_chosen} is {search_on}.")

        # Fetch nutrition information from API
        st.subheader(f"{fruit_chosen} Nutrition Information")
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        if smoothiefroot_response.status_code == 200:
            st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        else:
            st.error(f"Could not fetch data for {search_on}. API responded with {smoothiefroot_response.status_code}.")


# Construct the SQL insert statement
my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
            values ('""" + ingredients_string + """','""" + name_on_order + """')"""

# Button to submit the order
time_to_insert = st.button('Submit Order')

if time_to_insert:
    # Execute the SQL insert statement
    session.sql(my_insert_stmt).collect()
    st.success('Your Smoothie is ordered!', icon="✅")





