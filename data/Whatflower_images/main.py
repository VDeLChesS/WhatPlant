import os
import requests
from bs4 import BeautifulSoup, Tag
import psycopg2

# Database connection setup
def connect_db():
    try:
        conn = psycopg2.connect(
            dbname="scrapingtooldb",
            user="postgres",
            password="Deluchka5770!",
            host="localhost",
            port="5432"
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

# Create table species if it doesn't exist
def create_table(conn):
    try:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS SpeciesWithImages (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                image TEXT
            );
        ''')
        conn.commit()
        cur.close()
    except Exception as e:
        print(f"Error creating table: {e}")

# Function to save images and insert plant details into the database
def save_species_to_db(conn, species_name, img_url):
    try:
        cur = conn.cursor()

        # Download image
        img_data = requests.get(img_url).content
        img_filename = f"{species_name}.png"
        with open(img_filename, 'wb') as handler:
            handler.write(img_data)

        # Insert plant name and image filename into the database
        cur.execute("INSERT INTO SpeciesWithImages (name, image) VALUES (%s, %s)", (species_name, img_filename))
        conn.commit()
        cur.close()
        print(f"Inserted {species_name} into the database and saved image {img_filename}.")
    except Exception as e:
        print(f"Error saving species to db: {e}")

# Function to scrape the species from the web page
def scrape_species(conn):
    url = "https://whatflower.net/"
    base_url = "https://whatflower.net"

    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to retrieve the webpage.")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all figure elements with plant species
    for figure in soup.find_all('figure', class_='wp-caption'):
        # Extract the species name from the figcaption element
        figcaption = figure.find('figcaption', class_='wp-caption-text')
        if figcaption:
            species_name = figcaption.get_text().strip()

            # Find the image src
            img_tag = figure.find('img')
            if img_tag and 'src' in img_tag.attrs:
                img_src = img_tag['src']
                img_url = base_url + img_src  # Construct full image URL
                
                # Save species name and image to the database
                save_species_to_db(conn, species_name, img_url)

def main():
    conn = connect_db()
    if conn:
        create_table(conn)
        scrape_species(conn)
        conn.close()
    else:
        print("Database connection failed. Exiting.")

if __name__ == "__main__":
    main()