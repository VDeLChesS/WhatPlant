import os
import requests
from bs4 import BeautifulSoup

# Function to download and save images
def save_image(species_name, img_url):
    try:
        # Ensure the images directory exists
        if not os.path.exists('images'):
            os.makedirs('images')

        # Download image
        img_data = requests.get(img_url).content
        img_filename = f"images/{species_name}.png"
        with open(img_filename, 'wb') as handler:
            handler.write(img_data)

        print(f"Saved image {img_filename}.")
    except Exception as e:
        print(f"Error saving image {species_name}: {e}")

# Function to scrape the species from the web page
def scrape_species():
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
                
                # Save species name and image to the folder
                save_image(species_name, img_url)

def main():
    scrape_species()

if __name__ == "__main__":
    main()

