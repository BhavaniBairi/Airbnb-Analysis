import streamlit as st
from PIL import Image
from streamlit_option_menu import option_menu
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import seaborn as sns
import folium
from folium.plugins import MarkerCluster

#Importing the Airbnb csv file
df = pd.read_csv("Airbnb_data1.csv")

img1 = Image.open(r"C:\Users\rajub\OneDrive\Desktop\Airbnb_logo.jpeg")
st.set_page_config(page_title="Airbnb Analysis", page_icon=img1, layout="wide", initial_sidebar_state="expanded")
st.write("")
logo = Image.open(r"C:\Users\rajub\OneDrive\Desktop\logo.png")

with st.sidebar:
    selected = option_menu(menu_title="Airbnb",
                           options = ["Home", "Explore Data", "Insights"],
                           icons= ["house", "globe-central-south-asia", "bar-chart"])
    
img_airbnb = Image.open(r"C:\Users\rajub\OneDrive\Desktop\download_airbnb.jpeg")
img_airbnb1 = Image.open(r"C:\Users\rajub\OneDrive\Desktop\airbnb_pic.jpeg")

if selected == "Home":
    col = st.columns((2,1), gap='medium')
    
    with col[0]:
        st.write('''Welcome to the Airbnb Data Visualization project!!''')            
        st.write('''The aim of this Project is to provide the Insights on Airbnb Data.''')           
        st.write(''':orange[Data Retrievel]: Utilizes the pymongo client to efficiently retrieve the Airbnb data from the MongoDB Atlas.''')          
        st.write(''':orange[Streamlit Interface]: Provides a streamlined web interface powered by Streamlit for easy data fetching, Exploration and analysis.''')           
        st.write(''':orange[Data Vizualization:] Offers various interactive Vizualisations to explore Airbnb analytics and insights.''')            
        st.write(''':orange[Power BI Report]: Provides the holistic view of the Airbnb Data and its patterns.''')
    
    with col[1]:
        st.image(img_airbnb, width=400)

    st.write("")
    
    with st.expander('About Airbnb', expanded=True):
        st.write('''
            - Airbnb an abbreviation of its original name, "Airbed and Breakfast" is an American company
            operating an online marketplace for short-and-long-term homestays and experiences in various countries and regions.
            - It acts as a broker and charges a commission from each booking. Airbnb was founded in 2008 by Brian Chesky, Nathan Blecharczyk, 
            and Joe Gebbia. It is the best-known company for short-term housing rentals.
            - By October 2013, Airbnb had served 9,000,000 guests since its founding in August 2008. Nearly 250,000 listings
            were added in 2013. It also announced a partnership with Concur, an expense reporting service for businesses, to make it easier for business
            travelers to report Airbnb stays as business expenses.
            - In November 2016, Airbnb launched "experiences", whereby users can use the platform to book activities.
            ''')
        
    with st.expander('About', expanded=False):
        st.write('''
        - Data: [Data Link](https://github.com/BhavaniBairi/Airbnb-Analysis).
        - :orange[**By**]: Bhavani Bairi
        - :orange[**Project**]: Airbnb Data Visualization
        ''')

if selected == "Explore Data":
    
    country = st.sidebar.multiselect('Select a Country',sorted(df.Country.unique()),sorted(df.Country.unique()))
    prop = st.sidebar.multiselect('Select Property_type',sorted(df.Property_type.unique()),sorted(df.Property_type.unique()))
    room = st.sidebar.multiselect('Select Room_type',sorted(df.Room_type.unique()),sorted(df.Room_type.unique()))
    price = st.sidebar.slider('Select Price',df.Price.min(),df.Price.max(),(df.Price.min(),df.Price.max()))
    
    # CONVERTING THE USER INPUT INTO QUERY
    query = f'Country in {country} & Room_type in {room} & Property_type in {prop} & Price >= {price[0]} & Price <= {price[1]}'
    
    # TOTAL LISTINGS BY COUNTRY CHOROPLETH MAP
    st.markdown("### :orange[Total Listings by Country.]")

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
                tooltip=f'{country}: {total_listings} Listings',
                icon=folium.Icon(color='blue')
            ).add_to(marker_cluster)
    
    # Function to generate a map for the country with listings
    def generate_country_map(country):
        # Filter listings by country
        country_listings = get_listings_for_country(country)

        country_map = folium.Map(location=country_coordinates[country], zoom_start=2, tiles='OpenStreetMap')

        # Create a marker cluster for the listings in the country
        marker_cluster = MarkerCluster().add_to(country_map)

        # Add markers for all listings in the country
        for _, listing in country_listings.iterrows():
            lat, lon = listing['Latitude'], listing['Longitude']
            price = listing['Price']
            review_score = listing['Review_scores']
            Amenities = listing['Amenities']
            popup_content = (
                            f"<b>{listing['Name']}</b> | <b>{listing["Property_type"]}</b> | <b>{listing["Room_type"]}</b> <br>"
                            f"<b>Price:</b> ${price} | <b>Total_beds:</b> {listing["Total_beds"]} | <b>Accomodates:</b> {listing["Accomodates"]} <br>"
                            f"<b>Rating:</b> {review_score}/100<br>"
                            f"<b>Amenities</b> {Amenities}" )

            popup = folium.Popup(popup_content, max_width=300)

            folium.CircleMarker(
                location=[lat, lon],
                radius=5,
                color='blue',
                fill=True,
                fill_color='blue',
                fill_opacity=0.5,
                popup=popup,
                tooltip=f"${price}"
                ).add_to(marker_cluster)
            
        return country_map
    
    # Using Streamlit to display the initial map with the country markers
    st.components.v1.html(m._repr_html_(), width=800, height=500)

    st.markdown("### :orange[Distribution of listings across different Countries.]")

    selected_country = st.selectbox('Select a Country', country_coordinates.keys())

    # When a country is selected, shows the country-specific map with listings
    if selected_country:
        country_map = generate_country_map(selected_country)
        st.components.v1.html(country_map._repr_html_(), width=800, height=500)

    st.markdown("### :orange[Price Analysis:]")

    # AVG PRICE IN COUNTRIES Choropleth
    country_df = df.query(query).groupby('Country',as_index=False)['Price'].mean()
    
    col = st.columns((2,2), gap='medium')
    with col[0]:

        fig = px.choropleth(data_frame=country_df, 
                            locations='Country', 
                            color='Price', 
                            hover_data=['Country', 'Price'], 
                            locationmode='country names',
                            title='Average Price of listings in Each Country',
                            color_continuous_scale='agsunset'
                            )
        
        fig.update_layout(geo=dict(bgcolor='#9dc2a7'))

        st.plotly_chart(fig,width=400)

    with col[1]:
        # AVG PRICE BY Property TYPE BARCHART
        pr_df = df.query(query).groupby('Property_type',as_index=False)['Price'].mean().sort_values(by='Price')

        fig = px.bar(data_frame=pr_df,
                        x='Property_type',
                        y='Price',
                        color='Price',
                        title='Average Price of listings in each Property type'
                    )
        st.plotly_chart(fig,use_container_width=True)

    # **Price Distribution and Outliers**
    st.markdown("### :orange[Price Distribution and Outliers]")
    fig_box = go.Figure()

    # Boxplot for Price distribution
    fig_box.add_trace(go.Box(y=df['Price'], name='Price Distribution', boxmean='sd'))
    fig_box.update_layout(title="Price Distribution with Outliers", yaxis_title="Price (USD)")
    st.plotly_chart(fig_box)

    # **Correlations: Price vs. Rating, Price vs. Reviews, Price vs. Availability**
    st.markdown("### :orange[Price vs. Other Variables]")
    correlation_data = pd.DataFrame({
        'Price': df['Price'],
        'Rating': df['Review_scores'],
        'No_of_reviews': df['No_of_reviews'],
        'Availability': df['Availability_365'],
        'Total_beds' : df['Total_beds'],
    })

    col = st.columns((2,2,2), gap='medium')


    with col[0]:

        # Price vs. Rating
        price_rating_chart = px.scatter(correlation_data, x='Price', y='Rating', title="Price vs. Rating", labels={'Price': 'Price (USD)', 'Rating': 'Rating'})
        st.plotly_chart(price_rating_chart)

    with col[1]:

        #Price vs. No_of_reviews
        price_No_of_reviews_chart = px.scatter(correlation_data, x='Price', y='No_of_reviews', title="Price vs. No_of_reviews", labels={'Price': 'Price (USD)', 'No_of_reviews': 'No_of_reviews'})
        st.plotly_chart(price_No_of_reviews_chart)

    with col[2]:

        # Price vs. Availability
        price_availability_chart = px.scatter(correlation_data, x='Price', y='Availability', title="Price vs. Availability", labels={'Price': 'Price (USD)', 'Availability': 'Availability (Days)'})
        st.plotly_chart(price_availability_chart)

    # **Correlation Heatmap (Price and other variables)**
    roomProperty_DF = df.query(query).groupby(['Property_type','Room_type'], as_index=False)['Price'].mean().sort_values(by='Price')


    # Pivot the dataframe to create a matrix for the heatmap
    heatmap_data = roomProperty_DF.pivot(index='Property_type', columns='Room_type', values='Price')

    # Set up the matplotlib figure
    plt.figure(figsize=(12, 10))

    # Create a seaborn heatmap
    ax = sns.heatmap(heatmap_data,
                annot=True, 
                cmap='YlOrRd', 
                fmt='.2f', 
                linewidths=0.5, 
                cbar_kws={'label': 'Price ($)'}
                )
    for label in ax.get_xticklabels():
        label.set_color('white')
    
    for label in ax.get_yticklabels():
        label.set_color('white')
  
    plt.gcf().set_facecolor('#0d2a3d')
    with st.container():
        st.markdown("<div style='background-color:#0d2a3d; padding: 20px; border-radius: 5px; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);'><h3 style='color:#f5ad42;'>Price Heatmap</h3></div>", unsafe_allow_html=True)
    
    plt.title('### :orange[Average Price Heatmap by Property Type and Room Type]')

    # Display the heatmap in Streamlit
    st.pyplot(plt)

    st.markdown("### :orange[Correlation Heatmap]")
    correlation_matrix = correlation_data.corr()
    fig_corr = go.Figure(data=go.Heatmap(z=correlation_matrix.values, 
                                        x=correlation_matrix.columns, 
                                        y=correlation_matrix.columns, 
                                        colorscale='Viridis', 
                                        zmin=-1, zmax=1))
    fig_corr.update_layout(title="Correlation Heatmap of Price with Other Variables")
    st.plotly_chart(fig_corr)

    st.markdown("### :orange[Filter Listings by Price Range]")

    price_range = st.slider(
        "Select Price Range", 
        min_value=int(df['Price'].min()), 
        max_value=int(df['Price'].max()), 
        value=(int(df['Price'].min()), int(df['Price'].max())), 
        step=10
    )

    # Extract the selected minimum and maximum price from the tuple
    price_min, price_max = price_range

    filtered_df = df[(df['Price'] >= price_min) & (df['Price'] <= price_max)]
    st.write(f"Showing listings with price between {price_min} and {price_max} USD.")
    st.write(filtered_df)

    # Distribution of Availability
    st.markdown("")
    st.markdown("### :orange[Distribution of Availability]")
    plt.figure(figsize=(10,3))
    sns.histplot(df['Availability_30'], bins=30, kde=True, color='skyblue', label='30 Days')
    sns.histplot(df['Availability_60'], bins=30, kde=True, color='orange', label='60 Days')
    sns.histplot(df['Availability_90'], bins=30, kde=True, color='green', label='90 Days')
    sns.histplot(df['Availability_365'], bins=30, kde=True, color='red', label='365 Days')
    plt.title('Distribution of Availability (30, 60, 90, 365 Days)', fontsize=4)
    plt.xlabel('Availability in Days', fontsize=4)
    plt.ylabel('Number of Listings', fontsize=4)
    plt.legend()
    plt.grid(True)
    plt.xticks(fontsize=4)
    plt.yticks(fontsize=4)
    # Display the plot in Streamlit
    st.pyplot(plt)


    #Occupancy Rate Analysis
    st.markdown("### :orange[Occupancy Rate Analysis]")

    df['Booked_30'] = 30 - df['Availability_30']  
    df['Booked_60'] = 60 - df['Availability_60']  
    df['Booked_90'] = 90 - df['Availability_90']  
    df['Booked_365'] = 365 - df['Availability_365']                     

    df['Occupancy_Rate_30'] = (df['Booked_30'] / 30) * 100
    df['Occupancy_Rate_60'] = (df['Booked_60'] / 60) * 100
    df['Occupancy_Rate_90'] = (df['Booked_90'] / 90) * 100
    df['Occupancy_Rate_365'] = (df['Booked_365'] / 365) * 100

    col = st.columns((2,0.5,2), gap='medium')
    with col[0]:

        # Plotting the Distribution of Occupancy Rate for 30, 60, 90, and 365 Days
        fig = px.histogram(df, x="Occupancy_Rate_30", nbins=30, title="Occupancy Rate Distribution (30 Days)",
                        labels={"Occupancy_Rate_30": "Occupancy Rate (%)"})
        fig.update_layout(
            xaxis_title="Occupancy Rate (%)",
            yaxis_title="Number of Listings",
            bargap=0.2,
            height=400
        )
        st.plotly_chart(fig)
    
    with col[2]:

        # Occupancy Rate by Property Type and Room Type
        occupancy_by_property = df.groupby(['Property_type', 'Room_type'])[['Occupancy_Rate_30']].mean().reset_index()

        # Plotting with Plotly
        fig = px.bar(occupancy_by_property, x="Property_type", y="Occupancy_Rate_30", color="Room_type",
                    title="Average Occupancy Rate (30 Days) by Property and Room Type",
                    labels={"Occupancy_Rate_30": "Average Occupancy Rate (%)"},
                    barmode="group")
        fig.update_layout(
            xaxis_title="Property Type",
            yaxis_title="Average Occupancy Rate (%)",
            height=400,
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig)
   

if selected == "Insights":
    country = st.sidebar.multiselect('Select a Country',sorted(df.Country.unique()),sorted(df.Country.unique()))
    prop = st.sidebar.multiselect('Select Property_type',sorted(df.Property_type.unique()),sorted(df.Property_type.unique()))
    room = st.sidebar.multiselect('Select Room_type',sorted(df.Room_type.unique()),sorted(df.Room_type.unique()))
    price = st.sidebar.slider('Select Price',df.Price.min(),df.Price.max(),(df.Price.min(),df.Price.max()))
    
    # CONVERTING THE USER INPUT INTO QUERY
    query = f'Country in {country} & Room_type in {room} & Property_type in {prop} & Price >= {price[0]} & Price <= {price[1]}'

    # CREATING COLUMNS
    col1,col2,col3 = st.columns(3,gap='medium')
    
    with col1:

        # AVG PRICE BY ROOM TYPE BARCHART
        st.markdown('###### :orange[The Average Price of the Entire home/apt is high compared to the other two Room types except in China]')
        pr_df = df.query(query).groupby('Room_type',as_index=False)['Price'].mean().sort_values(by='Price')
        fig = px.bar(data_frame=pr_df,
                        x='Room_type',
                        y='Price',
                        color='Price',
                        )
        st.plotly_chart(fig,use_container_width=True)
        
    with col2:
        
        # TOTAL LISTINGS IN EACH ROOM TYPES PIE CHART
        st.markdown('###### :orange[The Entire Home or Apt listings are the most common type of accommodation available on Airbnb, with the highest number of listings in this category]')
        df1 = df.query(query).groupby(["Room_type"]).size().reset_index(name="counts")
        fig = px.pie(df1,
                        names='Room_type',
                        values='counts',
                        color_discrete_sequence=px.colors.sequential.Rainbow
                    )
        fig.update_traces(textposition='outside', textinfo='value+label')
        st.plotly_chart(fig,use_container_width=True)

    with col3:
        # TOP 10 PROPERTY TYPES BAR CHART
        st.markdown("###### :orange[Among all property types, 'Apartment' stands out as the most common, leading in the number of listings available]")
        df1 = df.query(query).groupby(["Property_type"]).size().reset_index(name="Listings").sort_values(by='Listings',ascending=False)[:10]
        fig = px.bar(df1,
                        x='Listings',
                        y='Property_type',
                        orientation='h',
                        color='Property_type',
                        color_continuous_scale=px.colors.sequential.Agsunset)
        st.plotly_chart(fig,use_container_width=True) 
    
    # CREATING COLUMNS
    col1,col2,col3= st.columns(3,gap='medium')

    with col1:
        # TOP 10 HOSTS BAR CHART
        df2 = df.query(query).groupby(["Host_name"]).size().reset_index(name="Listings").sort_values(by='Listings',ascending=False)[:10]
        st.markdown('###### :orange[Top 10 Hosts with Highest number of Listings]')
        fig = px.bar(df2,
                        x='Listings',
                        y='Host_name',
                        orientation='h',
                        color='Host_name',
                        color_continuous_scale=px.colors.sequential.Agsunset)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig,use_container_width=True)  

    with col2:        
        # AVAILABILITY BY ROOM TYPE BOX PLOT
        st.markdown('###### :orange[Listings for Entire Home tend to have a higher occupancy rate, suggesting they are booked for most of the year]')
        fig = px.box(data_frame=df.query(query),
                        x='Room_type',
                        y='Availability_365',
                        color='Room_type'
                    )
        st.plotly_chart(fig,use_container_width=True)
        
    with col3:        
        
        # AVG AVAILABILITY IN COUNTRIES SCATTERGEO
        st.markdown('###### :orange[Average of availability in each country]')
        country_df = df.query(query).groupby('Country',as_index=False)['Availability_365'].mean()
        country_df.Availability_365 = country_df.Availability_365.astype(int)
        fig = px.scatter_geo(data_frame=country_df,
                                        locations='Country',
                                        color= 'Availability_365', 
                                        hover_data=['Availability_365'],
                                        locationmode='country names',
                                        size='Availability_365',
                                        color_continuous_scale='agsunset'
                            )
        st.plotly_chart(fig,use_container_width=True)


    

    