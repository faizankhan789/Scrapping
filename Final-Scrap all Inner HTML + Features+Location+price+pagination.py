import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Target website base URL
base_url = "https://www.pakwheels.com/used-cars/toyota-corolla/688?page="

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode (no GUI)
chrome_options.add_argument("--ignore-certificate-errors")  # Ignore SSL certificate errors

# Create a new Chrome browser instance
driver = webdriver.Chrome(options=chrome_options)

# Define features list
features_list = [
    "ABS", "Air Bags", "Air Conditioning", "Alloy Rims", "AM/FM Radio", "CD Player",
    "Cassette Player", "Cool Box", "Cruise Control", "Climate Control", "DVD Player",
    "Front Speakers", "Front Camera", "Heated Seats", "Immobilizer Key", "Keyless Entry",
    "Navigation System", "Power Locks", "Power Mirrors", "Power Steering", "Power Windows",
    "Rear Seat Entertainment", "Rear AC Vents", "Rear Speakers", "Rear Camera", "Sun Roof",
    "Steering Switches", "USB and Auxillary Cable"
]

# Create a CSV file to store the data
csv_file_path = "scraped_data.csv"

with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)

    # Write header row
    header_row = ["Make and Model", "Year", "Mileage", "Fuel Type", "Transmission", "Registered in", "Color", "Assembly",
                  "Engine Capacity", "Body Type", "Extra1", "Extra2"] + features_list + ["Location", "Price"]

    csv_writer.writerow(header_row)

    # Loop through each page and scrape data
    for page_number in range(1, 2):  # Assuming there are 10 pages, adjust as needed
        # Construct the URL for the current page
        url = base_url + str(page_number)

        # Load the website
        driver.get(url)

        # Wait for some time to let the page load
        driver.implicitly_wait(20)

        # Get the HTML content after JavaScript has executed
        html_content = driver.page_source

        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Specify the classes of the specific div and ul you want to scrape
        ul_class = "list-unstyled search-results search-results-mid next-prev car-search-results"
        div_child_class = "col-md-9 grid-style"
        anchor_tag_class = "car-name ad-detail-path"

        # List to store concatenated URLs
        concatenated_urls = []

        # Find all occurrences of the specific ul element
        ul_list = soup.find_all('ul', {'class': ul_class})

        # Check if any ul elements are found
        if ul_list:
            for ul_element in ul_list:
                # Find all occurrences of the specific div element within each ul
                specific_div_list = ul_element.find_all('div', {'class': div_child_class})

                # Check if any div elements are found within the ul
                if specific_div_list:
                    # Loop through each div element to find anchor tags
                    for specific_div in specific_div_list:
                        # Find all occurrences of the anchor tag within each div
                        anchor_tags = specific_div.find_all('a', {'class': anchor_tag_class})

                        # Check if any anchor tags are found within the div
                        if anchor_tags:
                            # Concatenate the href attributes with the base URL and store in the list
                            concatenated_urls.extend([urljoin("https://www.pakwheels.com/", anchor_tag.get('href')) for anchor_tag in anchor_tags])
                        else:
                            print(f"No anchor tags with class '{anchor_tag_class}' found within the div.")
                else:
                    print(f"No DIV elements with class '{div_child_class}' found within the ul.")
        else:
            print(f"No UL elements with class '{ul_class}' found.")

        # Loop through each URL and navigate to the link to perform additional scraping
        for index, link in enumerate(concatenated_urls, start=1):
            # Navigate to the link
            driver.get(link)

            # Wait for some time to let the page load (you might need to adjust this based on the website)
            driver.implicitly_wait(10)

            # Get the HTML content after JavaScript has executed
            inner_html_content = driver.page_source

            # Parse the inner HTML using BeautifulSoup
            inner_soup = BeautifulSoup(inner_html_content, 'html.parser')

            # Initialize variables to store inner HTML
            h1_inner_html = []
            table_td_inner_html = []
            odd_li_inner_html = []
            detail_sub_heading_inner_html = ""
            generic_green_tag_inner_html = ""

            try:
                # Scraping <h1> tag inside <div class="well">
                h1_tag = inner_soup.find('div', {'class': 'well'}).find('h1').text.strip()
                h1_inner_html.append(h1_tag)
            except AttributeError:
                print("Could not find <h1> tag inside <div class='well'>")

            try:
                # Scraping <table> with class="table table-bordered text-center table-engine-detail fs16"
                table_tag = inner_soup.find('table', {'class': 'table table-bordered text-center table-engine-detail fs16'})
                if table_tag:
                    # Find all occurrences of <td> within <tr> and store their inner HTML in the array
                    table_td_inner_html.extend([td_tag.text.strip() for tr_tag in table_tag.find_all('tr') for td_tag in tr_tag.find_all('td')])
            except AttributeError:
                print("Could not find <table> with class='table table-bordered text-center table-engine-detail fs16'")

            try:
                # Scraping <ul> with class="list-unstyled ul-featured clearfix"
                ul_featured = inner_soup.find('ul', {'class': 'list-unstyled ul-featured clearfix'})
                if ul_featured:
                    # Find all odd occurrences of <li> and store their inner HTML in the array
                    odd_li_inner_html.extend([li_tag.text.strip() for i, li_tag in enumerate(ul_featured.find_all('li')) if i % 2 == 1])
            except AttributeError:
                print("Could not find <ul> with class='list-unstyled ul-featured clearfix'")

            try:
                # Scraping <ul> with class="list-unstyled car-feature-list nomargin"
                ul_tag = inner_soup.find('ul', {'class': 'list-unstyled car-feature-list nomargin'})
                if ul_tag:
                    ul_inner_html = ul_tag.decode_contents()
            except AttributeError:
                print("Could not find <ul> with class='list-unstyled car-feature-list nomargin'")

            try:
                # Scraping <p class="detail-sub-heading"> and <a> tag inside it
                detail_sub_heading_tag = inner_soup.find('p', {'class': 'detail-sub-heading'})
                if detail_sub_heading_tag:
                    a_tag = detail_sub_heading_tag.find('a')
                    if a_tag:
                        detail_sub_heading_inner_html = a_tag.text.strip()
            except AttributeError:
                print("Could not find <p class='detail-sub-heading'> and <a> tag inside it")

            try:
                # Scraping <strong> tag with class="generic-green"
                generic_green_tag_tag = inner_soup.find('strong', {'class': 'generic-green'})
                if generic_green_tag_tag:
                    generic_green_tag_inner_html = generic_green_tag_tag.text.strip()
            except AttributeError:
                print("Could not find <strong> tag with class='generic-green'")

            # Compare the UL Inner HTML with features_list
            comparison_results = [1 if feature in ul_tag.stripped_strings else 0 for feature in features_list] if ul_tag else [0] * len(features_list)
            # Write data to CSV file
            csv_writer.writerow(h1_inner_html + table_td_inner_html + odd_li_inner_html + comparison_results + [detail_sub_heading_inner_html, generic_green_tag_inner_html])
            print(f"loop number{page_number}:")
    

# Close the browser
driver.quit()

print(f"Scraped data saved to {csv_file_path}")
