#Creates CSV file with the short name, concept ID, and data format of each record.

# Imports libraries
import requests
from bs4 import BeautifulSoup
import csv
import xml.etree.ElementTree as ET 

providers = ('','NOAA_NCEI','SCIOPS','AU_AADC','NSIDCV0','ORNL_DAAC','LARC_ASDC','LAADS','GES_DISC','OB_DAAC','SEDAC','JAXA','GHRC','GHRC_CLOUD','LARC','ECHO10_OPS','ESA','USGS_LTA','USGS','PODAAC','USGS_EROS','ASF','LPDAAC_ECS','LANCEMODIS','NSIDC_ECS','ASIPS','EUMETSAT','ISRO','CDDIS','NCCS','LM_FIRMS','MOPITT','LANCEAMSR2','OMINRT')

# Function to receive user input for the provider to view records from
def get_provider():
    in_list = False
    for num in range(1,34):
        print('Enter ' + str(num) + ' to view records from: ' + providers[num])
    while in_list == False:
        p_num = input() 
        try:
            if 0 < int(p_num) < 34:
                return providers[int(p_num)]
                in_list = True
            else:
                print('Error...Please try again')
        except:
            print('Error...Please try again')

# Function to count the number of records from a provider
def get_hits(provider):
    # Connects to the URL with hit information (XML)
    xml_pg = requests.get('https://cmr.earthdata.nasa.gov/search/collections?provider='+provider)
    root = ET.fromstring(xml_pg.content)
    hit_count = int(root[0].text)
    return hit_count

# Function for scraping information from provider's records
def provider_scrape(provider):
    print('Writing to csv file...')
    
    csv_file = provider+'_Scrape.csv'
    url = 'https://cmr.earthdata.nasa.gov/search/collections.json?provider='+provider+'&page_size=2000&offset='
    
    # Writes to a csv file
    with open(csv_file, mode='w') as test_scrape:
        # Creates a csv writer object
        write = csv.writer(test_scrape, lineterminator = '\n')

        #Writes the header
        header = ['Short Name','Concept ID','Data Format']
        print(header)
        write.writerow(header)
        
        hits = get_hits(provider)
        offset = 0
        
        while hits > 0:    
            # Connects to the URL with record information
            url = url+str(offset)

            page = requests.get(url).json()

            entry_num = 0

            # Loops through all records
            for entry in page.get('feed').get('entry'):# 'entry' tags are for records

                short_name = page.get('feed').get('entry')[entry_num]["short_name"]
                concept_id = page.get('feed').get('entry')[entry_num]["id"]
                original_format = page.get('feed').get('entry')[entry_num]['original_format']
                data_format = ''
                
                if original_format == 'ECHO10':
                    format_tag = 'dataformat'
                    # Collects and parses
                    id_page = requests.get('https://cmr.earthdata.nasa.gov/search/concepts/'+concept_id+'.native')
                    soup = BeautifulSoup(id_page.text, 'html.parser')

                    # Pulls text from the <dataformat> tag
                    data_format = soup.find(format_tag)
                    
                if original_format == 'DIF10':
                    format_tag = 'distribution_format'
                    # Collects and parses
                    id_page = requests.get('https://cmr.earthdata.nasa.gov/search/concepts/'+concept_id+'.native')
                    soup = BeautifulSoup(id_page.text, 'html.parser')

                    # Pulls text from the <distribution_format> tag
                    data_format = soup.find(format_tag)
                
                if original_format == 'DIF':
                    format_tag = 'distribution_format'
                    # Collects and parses
                    id_page = requests.get('https://cmr.earthdata.nasa.gov/search/concepts/'+concept_id+'.native')
                    soup = BeautifulSoup(id_page.text, 'html.parser')

                    # Pulls text from the <distribution_format> tag
                    data_format = soup.find(format_tag)

                if original_format == 'UMM_JSON':
                    try:
                        id_page = requests.get('https://cmr.earthdata.nasa.gov/search/concepts/'+concept_id+'.native').json()
                        data_format = id_page.get('Distributions')[0]['DistributionFormat']
                    except:
                        data_format = "None"
                    if str(data_format) == 'None':
                        try:
                            id_page = requests.get('https://cmr.earthdata.nasa.gov/search/concepts/'+concept_id+'.native').json()
                            data_format = id_page.get('ArchiveAndDistributionInformation').get('FileDistributionInformation')[0].get('Format')
                        except:    
                            data_format = "None"
                
                if original_format == 'ISO19115':
                    try:
                        id_page = requests.get('https://cmr.earthdata.nasa.gov/search/concepts/'+concept_id+'.native')
                        soup = BeautifulSoup(id_page.text, 'html.parser')
                        resource_format = soup.find("gmd:distributorformat")
                        data_format = resource_format.find('gco:characterstring')
                    except:    
                        data_format = "None"
                    if str(data_format) == 'None':
                        try:
                            id_page = requests.get('https://cmr.earthdata.nasa.gov/search/concepts/'+concept_id+'.native')
                            soup = BeautifulSoup(id_page.text, 'html.parser')
                            resource_format = soup.find("gmd:distributionformat")
                            data_format = resource_format.find('gco:characterstring')
                        except:    
                            data_format = "None"
                    
                row = [short_name, concept_id]
                  
                name = ''
                try:
                    # Uses .contents to pull out the <dataformat> tag’s children
                    name = data_format.contents[0]

                except:
                    name = str(data_format)
                    pass

                finally:
                    row.append(name)

                #Writes the data rows
                print("Entry number " + str(offset + entry_num) + ": " + str(row))
                write.writerow(row)
                entry_num += 1
            offset += 2000
            hits -= 2000
    print('Finished!')

# Main script
print("This program will create a csv file with the short name, concept ID, and data format of each record ")
print("in a provider's records.\n")

provider = get_provider() 

provider_scrape(provider)
