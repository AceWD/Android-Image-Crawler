# -*- coding: utf-8 -*-
import scrapy
import firebase_admin
from firebase_admin import credentials, db
import sys

"""
TODO:
1. Add another parent in the database below the name of the phone to seperate between image data/ OTA data / Driver Binaries. DONE
2. Update doesnt work. DONE
3. Make code flexible for the 3 links, 90% done. HTML parse doesnt work on the drivers site
3. Clean and improve the code
"""

def format_path(path):
    return path.replace('.',' ')

def determine_header_name(data, format_var=False):
    
    p = ""

    if 'Version' in data.keys():
        p = 'Version'
    elif 'Description' in data.keys():
        p = 'Description'
    elif 'Hardware Component' in data.keys():
        p = 'Hardware Component'

    if format_var is True:
        return format_path(data[p])
    else:
        print(p)
        return data[p]

def add_to_database(db_ref, data, name, data_type):
        
        
        print(data)
        print("\t[+] Added " + data_type + " " + determine_header_name(data))
        

        
        #formated_version = data['version'].replace('.',' ') # Firebase doesnt allow . as a key paramater
        db_ref.child(name).child(data_type).child(determine_header_name(data, True)).set(data)


def update_phone(db_ref, data, name, data_type):
    print("\t[+] Updated " + determine_header_name(data))
    #phones/phonename/version
    db_ref.child(name).child(data_type).child(determine_header_name(data, True)).update(data)



def prase_info(response, data_type):
    
    cloud_phones = {}
    phones_to_upload = []

    phones = db.reference("Phones")
    result = phones.order_by_key().get()

    # Gets all the phones that are currently in the database
    print("[*] Getting phones from the database...")
    if result is not None:
        for phone_name, cloud_data in result.items():
            cloud_phones[phone_name] = cloud_data
            #print("Phone_name: " + phone_name + " cloud:data: " + str(cloud_data))

    #print("Values: " + str(cloud_phones.values()))   
    #print("Items: " + str(cloud_phones.items()))

    print("[*] Done loading phones from the database!")

    print("[*] Starting data analysis...")
    #Cycling through all the tables inside the page
    try:
        for table in response.xpath('//table'):

        
            label = table.xpath('./preceding-sibling::h2[1]/text()').extract()[0] # takes the phones name
            #print("Label: " + str(label))
            #print("[*] Checking if " + label + " versions need to be added or updated...")
            #for head in table.xpath('./tr/th'):
            th_data = table.xpath('.//thead/th/text()').extract() # Gets the header of the table
            
            #print("TH data: " + str(th_data))

            for values in table.xpath('.//tr'): # cycles through the tables values ( version, link, checksum )

                td_data = values.xpath('.//td/text()').extract() # the version checksum
                if data_type == 'drivers':
                    th_data = table.xpath('.//th/text()').extract() # Gets the header of the table in the case that we are in the drivers page
                    print("LOOKASD: " + str(td_data))
                
                data = {}

                for ind, val in enumerate(td_data): # Parsing the table data inside a dictionary
                    
                    if th_data[ind] != "Download": # Because the link is not inside tr it will not show up in the td_data list, so we need to skip it
                        data[th_data[ind]] = td_data[ind]
                    else:
                        data[th_data[ind + 1]] = td_data[ind]


                        
                data["Download"] = values.xpath('.//td/a/@href').extract_first() # Inserting the link to the data dictionary

                """
                data = {
                    th_data[1] : values.xpath('.//td/a/@href').extract_first(), # link
                    th_data[0] : td_data[0], # Version
                    th_data[2] : td_data[1] # Checksum
                }
                """
                """
                matchings = []
                for s in cloud_phones.items():
                    #print("KEYS: " + str(s[1][data_type].keys()))
                    #print("KEY: " + str(format_path(data['version'])))
                    test = format_path(data['version'])
                    if test in s[1][data_type].keys():
                        if s[1][data_type][format_path(data['version'])] == data:
                            #print("BLASdf")
                            matchings.append(s[1][data_type][format_path(data['version'])])
                    #if s[1][data_type] == data:
                """
                #matching = [x[1][data_type][format_path(data['version'])] for x in cloud_phones.items() if format_path(data['version']) in x[1][data_type].keys() if x[1][data_type][format_path(data['version'])] == data ]
                #print("MATCHH: " + str(matching))

                
                #print("Look here: " + str(cloud_phones.iteritems()))
                #
                if label not in cloud_phones.keys() or data_type not in cloud_phones[label]:  # Check if the phone is in the database or if the category (Image, OTA, Drivers) exists in the database
                    if 'crosshatch' in label:
                        add_to_database(phones, data, label, data_type)
                        phones_to_upload.append(data)

                elif cloud_phones[label][data_type][format_path(data[th_data[0]])] != data: # Check if the data the crawler got matches the cloud
                    update_phone(phones, data, label, data_type)
                
                #elif :
                #    print("DAATAAAA")
                #    add_to_database(phones, data, label, data_type)
                     
                #elif data['version'] not in cloud_phones.items().keys(): # One of the categories ( Image, OTA, Driver) Doesnt exists in the phone hirachy
                    

                
                    #print("[+] Adding " + label + " to the database")
                    phones_to_upload.append(data)
                #else:
                    #print(data)
                #yield data
                
                
    except KeyboardInterrupt:
        sys.exit()



class Factorybotspider(scrapy.Spider):

    name = 'factorybot'
    #allowed_domains = ['developers.google.com/android/images']#
    start_urls = ['https://developers.google.com/android/images',
                'https://developers.google.com/android/ota',
                'https://developers.google.com/android/drivers']
                

    cred = credentials.Certificate("./firmwarecrawler/web-crawler-3cde1-firebase-adminsdk-dhqns-deebae7e08.json")
    app = firebase_admin.initialize_app(cred,{
        'databaseURL': 'https://web-crawler-3cde1.firebaseio.com/'
    })


    
    

    def parse(self, response):
        page = response.url.split("/")[-1]
        #print("Page:" + str(page))
        prase_info(response, page)
        """
        cloud_phones = {}
        phones_to_upload = []

        phones = db.reference("Phones")
        result = phones.order_by_key().get()

        # Gets all the phones that are currently in the database
        print("[*] Getting phones from the database...")
        for phone_name, cloud_data in result.items():
            cloud_phones[phone_name] = cloud_data
            #print("Phone_name: " + phone_name + " cloud:data: " + str(cloud_data))

        print("[*] Done loading phones from the database!")

        print("[*] Starting data analysis...")
        #Cycling through all the tables inside the page
        for table in response.xpath('//table'):
            
            label = table.xpath('./preceding-sibling::h2[1]/text()').extract()[0] # takes the phones name

            print("[*] Checking if " + label + " versions need to be added or updated...")

            for values in table.xpath('.//tr'): # cycles through the tables values ( version, link, checksum )
                
                td_data = values.xpath('.//td/text()').extract() # the version checksum
                
                data = {
                    'link' : values.xpath('.//td/a/@href').extract_first(),
                    'version' : td_data[0],
                    'checksum' : td_data[1]
                }

                if label not in cloud_phones.keys(): # Check if the phone is in the database
                    add_to_database(phones, data, label)
                    phones_to_upload.append(data)

                elif cloud_phones[label] != data: # Check if the data the crawler got matches the cloud
                    update_phone(phones, data, label)
                    #print("[+] Adding " + label + " to the database")
                    phones_to_upload.append(data)
                #else:
                    #print(data)
                #yield data
    
    


        
        
        #print(all_phones[0])
        """
       
