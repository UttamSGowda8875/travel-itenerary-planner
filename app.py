import streamlit as st
import sqlite3
import pandas as pd
import os

if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None
if 'is_admin' not in st.session_state:
    st.session_state['is_admin'] = False
if 'additional_destinations' not in st.session_state:
    st.session_state['additional_destinations'] = {}

def init_db():
    conn = sqlite3.connect('app.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            contact_number TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            contact_info TEXT,
            cultural_interests TEXT,
            languages_spoken TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            review TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def add_review(user_id, review):
    conn = sqlite3.connect('app.db')
    c = conn.cursor()
    c.execute("INSERT INTO reviews (user_id, review) VALUES (?, ?)", (user_id, review))
    conn.commit()
    conn.close()

def get_reviews():
    conn = sqlite3.connect('app.db')
    c = conn.cursor()
    c.execute("SELECT u.username, r.review FROM reviews r JOIN users u ON r.user_id = u.id")
    reviews = c.fetchall()
    conn.close()
    return reviews

def admin_add_destination():
    if st.session_state.get('is_admin'):
        with st.form("add_destination"):
            new_destination = st.text_input("Destination Name")
            destination_info = st.text_area("Destination Information")
            submit_button = st.form_submit_button("Add Destination")

            if submit_button:
                st.session_state.additional_destinations[new_destination] = destination_info
                st.success(f"Destination {new_destination} added successfully!")
    else:
        st.error("You must be an admin to add a new destination.")

if 'reviews' not in st.session_state:
    st.session_state.reviews = [
        {'name': 'Alice', 'review': 'Great experience!'},
        {'name': 'Bob', 'review': 'Wonderful trip.'},
        {'name': 'Charlie', 'review': 'Amazing service!'}
    ]

def get_user_profile(user_id):
    conn = sqlite3.connect('app.db')
    c = conn.cursor()
    c.execute("SELECT name, contact_info, cultural_interests, languages_spoken FROM profiles WHERE user_id = ?", (user_id,))
    profile = c.fetchone()
    conn.close()
    return profile

def user_profile():
    if 'user_id' in st.session_state and st.session_state['user_id'] is not None:
        conn = sqlite3.connect('app.db')
        c = conn.cursor()
        c.execute("SELECT name, contact_info, cultural_interests, languages_spoken FROM profiles WHERE user_id = ?", (st.session_state['user_id'],))
        profile = c.fetchone()
        conn.close()
        current_profile = profile if profile else [None, None, None, None]
    else:
        current_profile = [None, None, None, None]
    with st.form("user_profile"):
        name = st.text_input("Name", value=current_profile[0] if current_profile[0] else '')
        contact_info = st.text_input("Contact Information", value=current_profile[1] if current_profile[1] else '')
        cultural_interests = st.text_area("Cultural Interests", value=current_profile[2] if current_profile[2] else '')
        languages_spoken = st.text_input("Languages Spoken", value=current_profile[3] if current_profile[3] else '')
        submit_button = st.form_submit_button("Update Profile")
        if submit_button:
            conn = sqlite3.connect('app.db')
            c = conn.cursor()
            c.execute("REPLACE INTO profiles (user_id, name, contact_info, cultural_interests, languages_spoken) VALUES (?, ?, ?, ?, ?)", 
                      (st.session_state['user_id'], name, contact_info, cultural_interests, languages_spoken))
            conn.commit()
            conn.close()
            st.success("Profile Updated!")

def destination_selection():
    all_destinations = ["Select Destination", "Zambia", "DR Congo", "Bali", "UAE", "Mexico"] + list(st.session_state.additional_destinations.keys())
    selected_destination = st.selectbox("Choose your destination:", all_destinations, key="destination_select")
    
    if selected_destination != "Select Destination":
        st.subheader(f"Explore {selected_destination}")
        if selected_destination in st.session_state.additional_destinations:
            st.write(st.session_state.additional_destinations[selected_destination])
        else:
            cultural_immersion(selected_destination)
        display_destination_image(selected_destination)
        download_itinerary_button(selected_destination)

def display_destination_image(destination):
    image_file = f"/Users/uttamsgowda/Downloads/DBMS-PROJECT/{destination.lower().replace(' ', '_')}.jpg"
    if os.path.isfile(image_file):
        st.image(image_file, caption=f"{destination}", use_column_width=True)


def download_itinerary_button(destination):
    itinerary_file = f"/Users/uttamsgowda/Downloads/DBMS-PROJECT/{destination.lower().replace(' ', '_')}.pdf"
    if os.path.isfile(itinerary_file):
        with open(itinerary_file, "rb") as file:
            st.download_button(
                label="Download Itinerary",
                data=file,
                file_name=itinerary_file,
                mime="application/pdf",
                key=f"download_{destination.replace(' ', '_')}"
            )


def cultural_immersion(destination):
    st.write(f"Cultural Immersion in {destination}")
    if destination == "Zambia":
        st.write(f'''
            Cultural immersion in Zambia offers a unique and enriching experience, 
            deeply rooted in the country's diverse traditions and ways of life. 
            Visitors have the opportunity to engage with local communities through 
            village visits and homestays, participate in vibrant traditional festivals 
            like the Kuomboka and Ncwala ceremonies, and explore Zambian arts and crafts 
            in local markets. Culinary experiences highlight traditional dishes, and 
            language learning opportunities foster deeper connections. The integration 
            of nature and wildlife through eco-cultural tours emphasizes Zambia's 
            commitment to community-based tourism. Additionally, traditional music and 
            dance, along with educational programs, provide a comprehensive understanding 
            of Zambia's rich cultural tapestry, making the experience both immersive and 
            respectful of the local customs and traditions.
        ''')
    elif destination == "DR Congo":
        st.write(f'''
            Cultural immersion in the Democratic Republic of Congo (DRC) is a journey through a nation rich in African traditions and history. The experience is marked by vibrant music and dance, particularly the famous Congolese rumba, reflecting the country's diverse ethnic tapestry. Visitors can explore Kinshasa's bustling markets, offering authentic crafts and textiles, and engage with local artisans. The DRC's culinary scene is a blend of African flavors, where dishes like Pondu (cassava leaves) and Fufu (cassava dough) are staples. The country's tumultuous history is showcased in museums and historical sites, providing a deeper understanding of its past and present. The Congo River and its surrounding landscapes offer a natural backdrop to the cultural exploration, with opportunities to visit remote communities and understand their connection to the environment.
        ''')
    elif destination == "Bali":
        st.write(f'''
            In Bali, cultural immersion is centered around the island's Hindu traditions, visible in its temples, rituals, and daily offerings. The artistic heritage is evident in Ubud, known for its dance performances, art galleries, and craft markets. Balinese cuisine, with dishes like Babi Guling (suckling pig) and Bebek Betutu (slow-cooked duck), offers a taste of the local flavors. Rice paddies and traditional farming practices provide insight into the agrarian lifestyle of many Balinese. The island's spirituality is experienced through yoga and meditation retreats, often set in serene landscapes. Learning opportunities abound, from cooking classes and woodcarving workshops to language lessons, allowing deeper engagement with the Balinese way of life.
        ''')
    elif destination == "UAE":
        st.write(f'''
            The United Arab Emirates (UAE) presents a cultural immersion that blends modernity with traditional Bedouin heritage. In cities like Dubai and Abu Dhabi, one can witness the marvels of contemporary architecture while also exploring historic districts and souks. The UAE's culinary landscape is a fusion of Middle Eastern and international cuisines, with local dishes like Harees and Shawarma. Cultural centers and museums, such as the Louvre Abu Dhabi, showcase both regional and global art. Traditional experiences include desert safaris, falconry, and camel riding, offering a glimpse into the Bedouin lifestyle. The UAE also hosts cultural festivals and events, reflecting its commitment to cultural diversity and global connectivity.
        ''')
    elif destination == "Mexico":
        st.write(f'''
            Cultural immersion in Mexico is a vibrant exploration of Mesoamerican history, Spanish colonial influence, and contemporary Mexican life. The country is renowned for its rich culinary heritage, featuring dishes like Tacos, Mole, and Chiles en Nogada. Artistic expressions are visible in the works of Frida Kahlo and Diego Rivera, and in the thriving street art scenes. Traditional markets, such as those in Oaxaca and Mexico City, provide a colorful array of crafts, textiles, and local produce. Festivals like Dia de Muertos (Day of the Dead) and Cinco de Mayo offer a vivid display of Mexico's cultural traditions. Visiting ancient ruins like Teotihuacan and Chichen Itza provides insight into the pre-Hispanic civilizations, while interactions with indigenous communities reveal the diversity of Mexico's ethnic heritage.
        ''')
    

def community_reviews():
    st.subheader("Community Reviews and Experiences")
    reviews = get_reviews()
    for username, review_text in reviews:
        st.text_area(f"Review by {username}", review_text, height=100, disabled=True)

    st.subheader('Add Your Review')
    review = st.text_area('Your Review')
    if st.button('Submit Review'):
        if 'user_id' in st.session_state and st.session_state['user_id']:
            add_review(st.session_state['user_id'], review)
            st.success('Thank you for your review!')
        else:
            st.error('You need to be logged in to submit a review.')

    # Join Query
    if st.session_state.get('is_admin'):
        st.subheader("User Profiles with Reviews")
        if st.button("Show Profiles and Reviews", key="join_query"):
            conn = sqlite3.connect('app.db')
            c = conn.cursor()
            query = """
            SELECT u.username, p.name, r.review
            FROM users u
            JOIN profiles p ON u.id = p.user_id
            JOIN reviews r ON u.id = r.user_id
            """
            c.execute(query)
            results = c.fetchall()
            if results:
                for result in results:
                    st.write(f"Username: {result[0]}, Name: {result[1]}, Review: {result[2]}")
            else:
                st.write("No user profiles with reviews found.")
            conn.close()



def about_us():
    st.subheader('About Us')
    st.write("""
        Traveleer is a travel company dedicated to bringing unique and memorable travel experiences to our clients. 
        Our mission is to make travel more accessible, comfortable, and enlightening. 
        We specialize in curated trips that cater to the interests and needs of our travelers, 
        ensuring each journey is unforgettable.
        
        Founded in 2023, Traveleer has grown from a small startup to a leading name in the travel industry. 
        Our team of travel experts works tirelessly to craft the perfect itineraries, 
        whether you're seeking adventure, relaxation, culture, or all of the above.
        
        Join us in exploring the wonders of the world!
    """)

def home_page():
    
    st.write("Welcome to Traveleer! Explore the world with us.")

    st.write("Discover new destinations, cultures, and experiences.")
    image_path = "/Users/uttamsgowda/Downloads/DBMS-PROJECT/travel.jpg"
    if os.path.isfile(image_path):
        st.image(image_path, use_column_width=True)
    else:
        st.write("Homepage image not found.")

def admin_login():
    with st.form("admin_login"):
        admin_password = st.text_input("Admin Password", type="password")
        submit_button = st.form_submit_button("Admin Login")
        if submit_button and admin_password == "your_admin_password":
            st.session_state['is_admin'] = True
            st.success("Admin logged in successfully!")
        elif submit_button:
            st.error("Incorrect password!")

def user_registration():
    with st.form("user_registration"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        email = st.text_input("Email")
        contact_number = st.text_input("Contact Number")
        address = st.text_area("Address")
        travel_preferences = st.text_area("Travel Preferences")
        submit_button = st.form_submit_button("Register")

        if submit_button:
            conn = sqlite3.connect('app.db')
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password, email, contact_number) VALUES (?, ?, ?, ?)", 
                  (username, password, email, contact_number))
            conn.commit()
            conn.close()
            st.success("Registered successfully!")

def user_login():
    with st.form("user_login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")

        if submit_button:
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                st.session_state['is_admin'] = True
                st.session_state['user_id'] = None
                st.session_state['username'] = username
                st.success("Admin logged in successfully!")
            else:
                conn = sqlite3.connect('app.db')
                c = conn.cursor()
                c.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
                result = c.fetchone()
                conn.close()

                if result:
                    st.session_state['user_id'] = result[0]
                    st.session_state['username'] = username
                    st.session_state['is_admin'] = False
                    st.success(f"Welcome, {username}")
                else:
                    st.error("Invalid username or password")


def remove_user(user_id):
    try:
        user_id = int(user_id)
    except ValueError:
        st.error("Invalid User ID format. It should be a number.")
        return

    conn = sqlite3.connect('app.db')
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id = ?", (user_id,))
    rows_affected = c.rowcount
    conn.commit()
    conn.close()

    if rows_affected > 0:
        st.success(f"Removed user with ID {user_id}")
    else:
        st.error(f"No user found with ID {user_id}")


def display_user_info():
    st.subheader("User Information")
    conn = sqlite3.connect('app.db')
    c = conn.cursor()
    c.execute("SELECT id, username, email, contact_number FROM users")
    users_info = c.fetchall()

    for user_info in users_info:
        user_id, username, email, contact_number = user_info
        st.text(f"ID: {user_id}, Username: {username}, Email: {email}, Contact: {contact_number}")
        if st.button(f"Remove {username}", key=f"remove_{user_id}"):
            remove_user(user_id)
            st.experimental_rerun()

    # Nested Query
    if st.button("Show users with reviews", key="nested_query"):
        c.execute("""
        SELECT username FROM users
        WHERE id IN (SELECT user_id FROM reviews)
        """)
        users_with_reviews = c.fetchall()
        if users_with_reviews:
            for user in users_with_reviews:
                st.write(user[0])
        else:
            st.write("No users with reviews found.")
    conn.close()


def display_all_users():
    st.subheader("Registered Users")
    conn = sqlite3.connect('app.db')
    c = conn.cursor()

    # Aggregate Query
    query = """
    SELECT u.id, u.username, u.email, u.contact_number, p.cultural_interests, p.languages_spoken
    FROM users u
    LEFT JOIN profiles p ON u.id = p.user_id
    """
    c.execute(query)
    users = c.fetchall()

    df = pd.DataFrame(users, columns=['ID', 'Username', 'Email', 'Contact Number', 'Cultural Interests', 'Languages Spoken'])

    st.dataframe(df)

    st.subheader("Remove User")
    user_id_to_remove = st.text_input("Enter User ID to Remove")
    if st.button("Remove User"):
        if user_id_to_remove:
            remove_user(user_id_to_remove)
        else:
            st.error("Please enter a valid User ID")

    # Aggregate Queries
    if st.button("Show number of reviews per user", key="aggregate_query"):
        conn = sqlite3.connect('app.db')
        c = conn.cursor()
        query = """
        SELECT u.username, COUNT(r.id) as review_count
        FROM users u
        LEFT JOIN reviews r ON u.id = r.user_id
        GROUP BY u.id
        """
        c.execute(query)
        results = c.fetchall()
        for result in results:
            st.write(f"Username: {result[0]}, Number of Reviews: {result[1]}")
        conn.close()

    conn.close()

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"

st.title('Traveleer')
st.sidebar.title('Navigation')

is_logged_in = st.session_state['user_id'] is not None or st.session_state['is_admin']

if is_logged_in and st.sidebar.button('Logout'):
    st.session_state['user_id'] = None
    st.session_state['is_admin'] = False 
    st.experimental_rerun()  

nav_options = ['Home', 'Destination Selection', 'Community Reviews']

if not is_logged_in:
    nav_options.extend(['Register', 'Login'])
if 'user_id' in st.session_state and st.session_state['user_id'] is not None:
    nav_options.append('User Profile')
if st.session_state.get('is_admin'):
    nav_options.append('User Data')

nav = st.sidebar.radio('Go to', nav_options)

if nav == 'Home':
    home_page()
elif nav == 'User Profile':
    user_profile()
elif nav == 'Destination Selection':
    destination_selection()
elif nav == 'Community Reviews':
    community_reviews()
elif nav == 'Register':
    user_registration()
elif nav == 'Login':
    user_login()
elif nav == 'User Data':
    if st.session_state.get('is_admin'):
        display_all_users()
        admin_add_destination()
    else:
        st.error("You must be an admin to view this page.")

init_db()