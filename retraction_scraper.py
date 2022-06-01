import requests
import re
from bs4 import BeautifulSoup

s = requests.Session()
url="http://retractiondatabase.org/RetractionSearch.aspx"
r = s.get(url)
soup = BeautifulSoup(r.content, 'html.parser')


formdata = {
   '__VIEWSTATE': soup.find('input', attrs={'name': '__VIEWSTATE'})['value'],
   '__VIEWSTATEGENERATOR': soup.find('input', attrs={'name': '__VIEWSTATEGENERATOR'})['value'],
   '__EVENTVALIDATION': soup.find('input', attrs={'name': '__EVENTVALIDATION'})['value'],
   '__VIEWSTATEENCRYPTED': soup.find('input', attrs={'name': '__VIEWSTATEENCRYPTED'})['value'],

    "__EVENTTARGET": "btnSearch",
    "__EVENTARGUMENT": "",
    "__LASTFOCUS": "",
}

headers={"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",

    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36"
        }

def  scraper(country="France",from_date="",to_date=""):
    """
    This fonction scrap the retraction database
    parameters :
    @country : string
    @from_date : string
    @to_date : string

    return table of dictionnaries

    """
    formdata["txtSrchCountry"] = country
    if from_date:
        formdata["txtFromDate"] = from_date
    if to_date:
        formdata["txtToDate"] = to_date

    resp = s.post(url, data=formdata,headers=headers)
    soupResult = BeautifulSoup(resp.text, 'html5lib')
    table = soupResult.find("table", id = "grdRetraction")
    scraped_rows=[]
    rows = table.find_all("tr")
    if len(rows) > 1:

        for row in rows[1:]:
            scraped_row={}
            scraped_row["title"] = row.find('span',attrs = {'class':'rTitle'}).get_text()
            journal = row.find_all('span',attrs = {'class':'rJournal'})
            if len(journal) > 0 :
                journal = journal[1].get_text().strip(" ---")
                scraped_row["journal"] = journal
            scraped_row["publisher"] = row.find('span',attrs = {'class':'rPublisher'}).get_text()
            institutions = row.find_all('span',attrs = {'class':'rInstitution'})
            scraped_row["institutions"]=[]
            for institution in institutions:
                instit = institution.get_text().strip()
                if instit:
                    scraped_row["institutions"].append(instit)
            reasons = row.find_all('div',attrs = {'class':'rReason'})
            scraped_row["reasons"] =[]
            for reason in row.find_all('div',attrs = {'class':'rReason'}) : 
                scraped_row["reasons"].append(reason.get_text().strip("+"))
            scraped_row["authors"] = []
            for author in row.find_all('a',attrs = {'class':'authorLink'}) : 
                scraped_row["authors"].append(author.get_text())
            urls = row.find_all('span',attrs = {'class':'rNature'}) # [original doi, doi of retraction, nature of retraction]
            scraped_row["original_doi"] = urls [0].get_text()
            scraped_row["retraction_doi"] = urls [1].get_text()
            scraped_row["retraction_nature"] = urls [2].get_text()            
            cells = row.find_all("td")


            if len(cells) > 0:
                dateregex = re.compile("([0-9][0-9])/([0-9][0-9])/([0-9][0-9][0-9][0-9])")
                date_published = dateregex.search(cells[4].text)
                scraped_row["date_published"] = date_published.group(0)
                date_retract = dateregex.search(cells[5].text)
                scraped_row["date_retracted"] = date_retract.group(0)
                cell7 = str(cells[7]).split('<br/>')
                countries = []
                for country in cell7[0:-1]:
                    country = BeautifulSoup(country,'html5lib').text.strip()
                    countries.append(country)
                scraped_row["countries"] = countries
                paywalled = cell7[-1]
                scraped_row ["paywalled"] = BeautifulSoup(paywalled,'html5lib').text.strip()
            scraped_rows.append(scraped_row)
    return scraped_rows


def main():
    """
    """
    scraped = scraper(country="France",from_date="05/01/2022")
    print(scraped)
    


if __name__ == '__main__':
	main()


