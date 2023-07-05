import requests
from lxml import etree
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from django.shortcuts import render

# Set up Selenium ChromeDriver
chrome_options = Options()
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument("--headless")  # Run Chrome in headless mode
service = Service('path_to_chromedriver')  # Specify path to chromedriver executable
driver = webdriver.Chrome(service=service, options=chrome_options)

base_url = "https://nssr.kystportal.no/storskjerm.asp?_side={}"

def scraped_data_view(request):
    scraped_data = []

    for side in range(1, 3):  # Iterate over sides 1 and 2
        url = base_url.format(side)

        driver.get(url)

        
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div#txt_storskjerm table')))

        html_content = driver.page_source


        # Parse the HTML content using lxml
        tree = etree.HTML(html_content)

        # Find the first <td> element with attributes valign="top" and width="30%"
        td_elements = tree.xpath('//td[@valign="top" and @width="30%"]')[:2]

        for td_element in td_elements:
            # Find the table inside the <td> element using XPath
            table = td_element.xpath('./table/tbody/tr[2]/td/table/tbody')
            type_element = td_element.xpath('./table/tbody/tr[1]/td/b')

            if type_element:
                type_element = type_element[0]
                # Get the text content of the type element
                type_text = type_element.text
            else:
                type_text = ''

            if table:
                table = table[0]
                # Convert the table back to an XML string
                table_xml = etree.tostring(table, pretty_print=True).decode()

                # Process the table rows
                rows = table.xpath('./tr')
                for row in rows:
                    columns = row.xpath('./td')
                    if len(columns) == 6:  # Ensure the row has the expected number of columns
                        if columns[1].xpath('.//img'):  # Check if column[1] has an image
                            comment = 'yes'
                        else:
                            comment = 'no'

                        if side == 1:
                            region = 'Sør'
                        elif side == 2:
                            region = 'Nord'

                        status = columns[2].xpath('./@bgcolor')[0]  # Get the bgcolor attribute value

                        data = {
                            'town': columns[0].text.strip(),
                            'vessel': columns[2].text.strip(),
                            'pending': columns[4].text.strip() if columns[4].text else '0',
                            'phone_number': columns[5].text.strip() if columns[5].text else '',
                            'comment': comment,
                            'region': region,
                            'type': type_text,
                            'status': status
                        }
                        scraped_data.append(data)
            else:
                print("Table not found.")
        else:
            print("TD element not found.")

    return render(request, 'scraped_data.html', {'scraped_data': scraped_data})

