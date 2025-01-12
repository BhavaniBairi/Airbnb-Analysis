import streamlit as st
from PIL import Image
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns


df = pd.read_csv("Airbnb_data.csv")

img1 = Image.open(r"C:\Users\rajub\OneDrive\Desktop\Airbnb_logo.jpeg")

st.set_page_config(page_title="Airbnb Analysis", page_icon=img1, layout="wide", initial_sidebar_state="expanded")


st.write("")

logo = Image.open(r"C:\Users\rajub\OneDrive\Desktop\logo.png")

with st.sidebar:
    selected = option_menu(menu_title="Airbnb Analysis", menu_icon='view-stacked',
                           options = ["Home", "Explore Data", "Insights"],
                           icons= ["house", "globe-central-south-asia", "bar-chart"])
    
img_airbnb = Image.open(r"C:\Users\rajub\OneDrive\Desktop\download_airbnb.jpeg")
img_airbnb1 = Image.open(r"C:\Users\rajub\OneDrive\Desktop\airbnb_pic.jpeg")

if selected == "Home":
    col1, col2 = st.columns(2)
    with col1:
        st.image(img_airbnb, width=400)
    with col2:
        st.markdown('''Airbnb an abbreviation of its original name, "Airbed and Breakfast" is an American company
                     operating an online marketplace for short-and-long-term homestays and experiences in various countries and regions.
                     It acts as a broker and charges a commission from each booking. Airbnb was founded in 2008 by Brian Chesky, Nathan Blecharczyk, 
                    and Joe Gebbia. It is the best-known company for short-term housing rentals.''')
        st.markdown('''By October 2013, Airbnb had served 9,000,000 guests since its founding in August 2008.[22] Nearly 250,000 listings
                     were added in 2013.''')
        st.markdown('''Several studies have found that long-term rental prices in many areas have increased because landlords have kept 
                    properties off the longer-term rental market to instead get higher rental rates for short-term housing via Airbnb.''')
    


    st.write("")
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 =st.columns(2)

    with col1:
        st.markdown('''PhonePe Pulse platform showcases data from more than 2,000 crore transactions by
                     digital payment consumers in India, starting 2018. It will be updating this data quarterly,
                     and will open up platform application programming interfaces (APIs) to help developers
                     build better products from data insights on the platform.''')

    with col2:
        st.image(img_airbnb1, width=400)

if selected == "Explore Data":
    
    country = st.sidebar.multiselect('Select a Country',sorted(df.Country.unique()),sorted(df.Country.unique()))
    prop = st.sidebar.multiselect('Select Property_type',sorted(df.Property_type.unique()),sorted(df.Property_type.unique()))
    room = st.sidebar.multiselect('Select Room_type',sorted(df.Room_type.unique()),sorted(df.Room_type.unique()))
    price = st.sidebar.slider('Select Price',df.Price.min(),df.Price.max(),(df.Price.min(),df.Price.max()))

    # CONVERTING THE USER INPUT INTO QUERY
    query = f'Country in {country} & Room_type in {room} & Property_type in {prop} & Price >= {price[0]} & Price <= {price[1]}'
    
    # TOTAL LISTINGS BY COUNTRY CHOROPLETH MAP
    st.markdown("## :orange[Total Listings by country]")

    m = folium.Map()

    marker_cluster = MarkerCluster().add_to(m)

    country_df = df.query(query).groupby(['Country'],as_index=False)['Name'].count().rename(columns={'Name' : 'Total_Listings'})

    country_coordinates = {
                            'Australia': [-25.2744, 133.7751],
                            'Brazil': [-14.2350, -51.9253],
                            'Canada': [56.1304, -106.3468],
                            'China': [35.8617, 104.1954],
                            'Hong Kong': [22.3193, 114.1694],
                            'Portugal': [39.3999, -8.2245],
                            'Spain': [40.4637, -3.7492],
                            'Turkey': [38.9637, 35.2433],
                            'United States': [37.0902, -95.7129]
                        }


    def get_listings_for_country(country):
        return df[df["Country"]== country]
    
    for _, row in country_df.iterrows():
        country = row['Country']
        total_listings = row['Total_Listings']

        # Get coordinates for the country
        if country in country_coordinates:
            lat, lon = country_coordinates[country]
            
            # Add a marker for the country
            folium.Marker(
                location=[lat, lon],
                popup=f'{country}: {total_listings} Listings',
                icon=folium.Icon(color='blue')
            ).add_to(marker_cluster)

    
    # Function to generate a map for the country with listings
    def generate_country_map(country):
        # Filter listings by country
        country_listings = get_listings_for_country(country)
        
        # Create a new map centered on the country
        country_map = folium.Map(location=country_coordinates[country], zoom_start=2)

        # Create a marker cluster for the listings in the country
        marker_cluster = MarkerCluster().add_to(country_map)

        # Add markers for all listings in the country
        for _, listing in country_listings.iterrows():
            lat, lon = listing['Latitude'], listing['Longitude']
            price = listing['Price']
            review_score = listing['Review_scores']

            popup_content = f"{listing['Name']} | Price: ${price} | Review Score: {review_score}/100"

            folium.Marker(
                location=[lat, lon],
                popup=popup_content,
                icon=folium.Icon(color='green')
            ).add_to(marker_cluster)

        return country_map

    # Adding the interaction to the Streamlit app
    # Using Streamlit to display the initial map with the country markers
    st.components.v1.html(m._repr_html_(), width=800, height=600)

    st.markdown("")
    st.markdown("## :orange[Distribution of listings accross different Countries]")

    # When a country is selected, a new map is shown with all listings in that country
    selected_country = st.selectbox('Select a Country', list(country_coordinates.keys()))

    # When a country is selected, show the country-specific map with listings
    if selected_country:
        country_map = generate_country_map(selected_country)
        st.components.v1.html(country_map._repr_html_(), width=800, height=600)

    # HEADING 1
    st.markdown("## Price Analysis")

    # AVG PRICE IN COUNTRIES SCATTERGEO
    country_df = df.query(query).groupby('Country',as_index=False)['Price'].mean()
    fig = px.scatter_geo(data_frame=country_df,
                                    locations='Country',
                                    color= 'Price', 
                                    hover_data=['Price'],
                                    locationmode='country names',
                                    size='Price',
                                    title= 'Avg Price in each Country',
                                    color_continuous_scale='agsunset'
                        )
    st.plotly_chart(fig,use_container_width=True)
    
    # **Price Distribution and Outliers**
    st.subheader("Price Distribution and Outliers")
    fig_box = go.Figure()

    # Add boxplot for Price distribution
    fig_box.add_trace(go.Box(y=df['Price'], name='Price Distribution', boxmean='sd'))
    fig_box.update_layout(title="Price Distribution with Outliers", yaxis_title="Price (USD)")
    st.plotly_chart(fig_box)

    # **Correlations: Price vs. Rating, Price vs. Reviews, Price vs. Availability**
    st.subheader("Price vs. Other Variables")
    correlation_data = pd.DataFrame({
        'Price': df['Price'],
        'Rating': df['Review_scores'],
        'No_of_reviews': df['No_of_reviews'],
        'Availability': df['Availability_365']
    })

    # Price vs. Rating
    price_rating_chart = px.scatter(correlation_data, x='Price', y='Rating', title="Price vs. Rating", labels={'Price': 'Price (USD)', 'Rating': 'Rating'})
    st.plotly_chart(price_rating_chart)

    #Price vs. No_of_reviews
    price_No_of_reviews_chart = px.scatter(correlation_data, x='Price', y='No_of_reviews', title="Price vs. No_of_reviews", labels={'Price': 'Price (USD)', 'No_of_reviews': 'No_of_reviews'})
    st.plotly_chart(price_No_of_reviews_chart)

    # Price vs. Availability
    price_availability_chart = px.scatter(correlation_data, x='Price', y='Availability', title="Price vs. Availability", labels={'Price': 'Price (USD)', 'Availability': 'Availability (Days)'})
    st.plotly_chart(price_availability_chart)

    # **Correlation Heatmap (Price and other variables)**
    st.subheader("Correlation Heatmap")
    correlation_matrix = correlation_data.corr()
    fig_corr = go.Figure(data=go.Heatmap(z=correlation_matrix.values, 
                                        x=correlation_matrix.columns, 
                                        y=correlation_matrix.columns, 
                                        colorscale='Viridis', 
                                        zmin=-1, zmax=1))
    fig_corr.update_layout(title="Correlation Heatmap of Price with Other Variables")
    st.plotly_chart(fig_corr)

    st.subheader("Filter Listings by Price Range")

    price_range = st.slider(
        "Select Price Range", 
        min_value=int(df['Price'].min()), 
        max_value=int(df['Price'].max()), 
        value=(int(df['Price'].min()), int(df['Price'].max())), 
        step=10
    )

    # Extract the selected minimum and maximum price from the tuple
    price_min, price_max = price_range


    '''price_min = st.slider("Minimum Price", min_value=int(df['Price'].min()), max_value=int(df['Price'].max()), value=int(df['Price'].min()))
    price_max = st.slider("Maximum Price", min_value=int(df['Price'].min()), max_value=int(df['Price'].max()), value=int(df['Price'].max()))'''

    filtered_df = df[(df['Price'] >= price_min) & (df['Price'] <= price_max)]
    st.write(f"Showing listings with price between {price_min} and {price_max} USD.")
    st.write(filtered_df)
    
    # CREATING COLUMNS
    col1,col2 = st.columns(2,gap='medium')
    
    with col1:

        # AVG PRICE BY ROOM TYPE BARCHART
        pr_df = df.query(query).groupby('Room_type',as_index=False)['Price'].mean().sort_values(by='Price')
        fig = px.bar(data_frame=pr_df,
                        x='Room_type',
                        y='Price',
                        color='Price',
                        title='Avg Price in each Room type'
                    )
        st.plotly_chart(fig,use_container_width=True)

        # AVG PRICE BY Property TYPE BARCHART
        pr_df = df.query(query).groupby('Property_type',as_index=False)['Price'].mean().sort_values(by='Price')
        fig = px.bar(data_frame=pr_df,
                        x='Property_type',
                        y='Price',
                        color='Price',
                        title='Avg Price in each Property type'
                    )
        st.plotly_chart(fig,use_container_width=True)

        
        st.subheader("Distribution of Availability Over Different Time Periods")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.histplot(df['Availability_30'], kde=True, color='blue', label='Availability 30')
        sns.histplot(df['Availability_60'], kde=True, color='green', label='Availability 60')
        sns.histplot(df['Availability_90'], kde=True, color='orange', label='Availability 90')
        sns.histplot(df['Availability_365'], kde=True, color='red', label='Availability 365')
        ax.set_title('Distribution of Availability over Different Time Periods')
        ax.set_xlabel('Availability')
        ax.set_ylabel('Frequency')
        ax.legend()

        # Display the histogram in Streamlit
        st.pyplot(fig)

        # 3. **Box Plot** visualization
        st.subheader("Box Plot of Availability Across Time Periods")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.boxplot(data=df[['Availability_30', 'Availability_60', 'Availability_90', 'Availability_365']], ax=ax)
        ax.set_title('Box Plot of Availability across Time Periods')
        ax.set_ylabel('Availability')
        ax.set_xticklabels(['Availability 30', 'Availability 60', 'Availability 90', 'Availability 365'])

        # Display the box plot in Streamlit
        st.pyplot(fig)

        # 4. **Correlation Heatmap** visualization
        st.subheader("Correlation Heatmap of Availability over Different Time Periods")
        corr_matrix = df[['Availability_30', 'Availability_60', 'Availability_90', 'Availability_365']].corr()
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f', cbar=True, ax=ax)
        ax.set_title('Correlation Heatmap of Availability over Different Time Periods')

        # Display the heatmap in Streamlit
        st.pyplot(fig)

        # 5. **Pair Plot** visualization
        st.subheader("Pairwise Plot of Availability Across Time Periods")
        st.write("This plot shows pairwise relationships between different time periods.")
        sns.pairplot(df[['Availability_30', 'Availability_60', 'Availability_90', 'Availability_365']])
        st.pyplot(plt)

        # 6. **Line Plot Over Time** (Optional: if you have a date column)
        # Example (commented out as there's no Date column in this example):
        # st.subheader("Availability Over Time")
        # df['Date'] = pd.date_range(start='2023-01-01', periods=len(df), freq='D')
        # fig, ax = plt.subplots(figsize=(12, 6))
        # ax.plot(df['Date'], df['Availability_30'], label='Availability 30', color='blue')
        # ax.plot(df['Date'], df['Availability_60'], label='Availability 60', color='green')
        # ax.plot(df['Date'], df['Availability_90'], label='Availability 90', color='orange')
        # ax.plot(df['Date'], df['Availability_365'], label='Availability 365', color='red')
        # ax.set_title('Availability Over Time')
        # ax.set_xlabel('Date')
        # ax.set_ylabel('Availability')
        # ax.legend()
        # st.pyplot(fig)

        # TOP 10 PROPERTY TYPES BAR CHART
        df1 = df.query(query).groupby(["Property_type"]).size().reset_index(name="Listings").sort_values(by='Listings',ascending=False)[:10]
        fig = px.bar(df1,
                        title='Top 10 Property Types',
                        x='Listings',
                        y='Property_type',
                        orientation='h',
                        color='Property_type',
                        color_continuous_scale=px.colors.sequential.Agsunset)
        st.plotly_chart(fig,use_container_width=True) 
    
        # TOP 10 HOSTS BAR CHART
        df2 = df.query(query).groupby(["Host_name"]).size().reset_index(name="Listings").sort_values(by='Listings',ascending=False)[:10]
        fig = px.bar(df2,
                        title='Top 10 Hosts with Highest number of Listings',
                        x='Listings',
                        y='Host_name',
                        orientation='h',
                        color='Host_name',
                        color_continuous_scale=px.colors.sequential.Agsunset)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig,use_container_width=True)
    
    with col2:
        
        # TOTAL LISTINGS IN EACH ROOM TYPES PIE CHART
        df1 = df.query(query).groupby(["Room_type"]).size().reset_index(name="counts")
        fig = px.pie(df1,
                        title='Total Listings in each Room_types',
                        names='Room_type',
                        values='counts',
                        color_discrete_sequence=px.colors.sequential.Rainbow
                    )
        fig.update_traces(textposition='outside', textinfo='value+label')
        st.plotly_chart(fig,use_container_width=True)
        
        

    
    
    st.markdown("## Explore more about the Airbnb data")

    
    

    # CREATING COLUMNS
    col1,col2 = st.columns(2,gap='medium')

    with col1:
        
        # AVG PRICE BY ROOM TYPE BARCHART
        pr_df = df.query(query).groupby('Room_type',as_index=False)['Price'].mean().sort_values(by='Price')
        fig = px.bar(data_frame=pr_df,
                        x='Room_type',
                        y='Price',
                        color='Price',
                        title='Avg Price in each Room type'
                    )
        st.plotly_chart(fig,use_container_width=True)
        
        # HEADING 2
        st.markdown("## Availability Analysis")
        
        # AVAILABILITY BY ROOM TYPE BOX PLOT
        fig = px.box(data_frame=df.query(query),
                        x='Room_type',
                        y='Availability_365',
                        color='Room_type',
                        title='Availability by Room_type'
                    )
        st.plotly_chart(fig,use_container_width=True)
        
    with col2:
        
        
        
        # BLANK SPACE
        st.markdown("#   ")
        st.markdown("#   ")
        
        # AVG AVAILABILITY IN COUNTRIES SCATTERGEO
        country_df = df.query(query).groupby('Country',as_index=False)['Availability_365'].mean()
        country_df.Availability_365 = country_df.Availability_365.astype(int)
        fig = px.scatter_geo(data_frame=country_df,
                                        locations='Country',
                                        color= 'Availability_365', 
                                        hover_data=['Availability_365'],
                                        locationmode='country names',
                                        size='Availability_365',
                                        title= 'Avg Availability in each Country',
                                        color_continuous_scale='agsunset'
                            )
        st.plotly_chart(fig,use_container_width=True)

    

    

    