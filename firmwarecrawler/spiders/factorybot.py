# -*- coding: utf-8 -*-
import scrapy
import firebase_admin
from firebase_admin import credentials, db

"""
TODO:
1. Add another parent in the database below the name of the phone to seperate between image data/ OTA data / Driver Binaries
2. Update doesnt work
3. Clean and improve the code
"""

def add_to_database(db_ref, data, name):
        print("\t[+] Added " + data['version'])
        formated_version = data['version'].replace('.',' ') # Firebase doesnt allow . as a key paramater
        db_ref.child(name).child(formated_version).set(data)


def update_phone(db_ref, data, name):
    print("\t[+] Updated " + data['version'])
    #phones/phonename/version
    #db_ref.child(name).child(data['version']).update(data)

class FactorybotSpider(scrapy.Spider):

    name = 'factorybot'
    allowed_domains = ['developers.google.com/android/images']#
    start_urls = ['https://developers.google.com/android/images']

    cred = credentials.Certificate("./firmwarecrawler/web-crawler-3cde1-firebase-adminsdk-dhqns-deebae7e08.json")
    app = firebase_admin.initialize_app(cred,{
        'databaseURL': 'https://web-crawler-3cde1.firebaseio.com/'
    })


    
    

    def parse(self, response):
        
        
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
        
       
