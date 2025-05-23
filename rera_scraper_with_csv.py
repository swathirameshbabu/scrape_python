import requests
from bs4 import BeautifulSoup
import time
import csv

BASE_URL = "https://rera.odisha.gov.in"
PROJECTS_LIST_URL = BASE_URL + "/projects/project-list"

headers = {
    "User-Agent": "Mozilla/5.0"
}

def get_project_links():
    response = requests.get(PROJECTS_LIST_URL, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    table_rows = soup.select("table#projectListTable tbody tr")
    project_links = []

    for row in table_rows[:6]:  # Only first 6 projects
        link_tag = row.find("a", string="View Details")
        if link_tag and link_tag.get("href"):
            project_links.append(BASE_URL + link_tag["href"])
    return project_links

def extract_project_details(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    def get_text(label):
        cell = soup.find("th", string=label)
        if cell and cell.find_next("td"):
            return cell.find_next("td").get_text(strip=True)
        return "Not Found"

    details = {
        "Rera Regd. No": get_text("RERA Registration Number"),
        "Project Name": get_text("Project Name"),
        "Promoter Name": get_text("Company Name"),
        "Promoter Address": get_text("Registered Office Address"),
        "GST No.": get_text("GST Number")
    }

    return details

if __name__ == "__main__":
    print("Fetching first 6 project links...")
    links = get_project_links()
    print("Extracting project details and writing to CSV...
")

    all_data = []
    for idx, link in enumerate(links, 1):
        print(f"Processing Project {idx}...")
        project_data = extract_project_details(link)
        all_data.append(project_data)
        time.sleep(2)

    csv_file = "rera_projects.csv"
    keys = all_data[0].keys()

    with open(csv_file, "w", newline='', encoding="utf-8") as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(all_data)

    print(f"Data saved to {csv_file}")
