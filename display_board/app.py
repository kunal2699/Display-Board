from flask import Flask, jsonify, render_template, jsonify, request
import requests
import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import urllib.request
from io import BytesIO
from PIL import Image
import os
import mimetypes

app = Flask(__name__)

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('', scope)# get the google cloud API linked with the Google sheet to get the data 

client = gspread.authorize(creds)

# get the instance of the Spreadsheet
sheet = client.open('') # Google Sheet name

# get the first sheet of the Spreadsheet
sheet_instance = sheet.get_worksheet(0)
 
city_visibility = {
    'Shimla': True, 
    'Sundernagar': True, 
    'Kangra': True, 
    'Keylong': True, 
    'Chamba': True, 
    'Kufri': True,
    'Kullu': True,
    'Kalpa': True
    # Default visibility status, you can set it as needed
    # Add more cities as needed
}

@app.route('/')
def home():
    records_data = sheet_instance.get_all_records()
    for record in records_data:
        if record['SosLink'] or record['SosMarquee']:
            return render_template('SOS.html')
        else:
            return render_template('index640.html', city_visibility=city_visibility)

@app.route('/admin')
def admin():  
    return render_template('admin.html')

@app.route('/update_visibility', methods=['POST'])
def update_visibility():
    global city_visibility
    data = request.json
    for city, visible in data.items():
        city_visibility[city] = visible
    return jsonify({'message': 'Visibility updated successfully'})

@app.route('/get_weather_data',methods=['GET', 'POST'])
def get_weather_data():
    url = "https://mausam.imd.gov.in/shimla/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    data = soup.find('div', {'class': 'capitals clearfix'})
    data = data.find('div', {'class': 'capital'})
    weather_data = []
    
    i = 0
    while i < 8:
        city = data.find('h3').text
        if city_visibility[city]:
            temp = data.find('p', {'class': 'now'}).text if data.find('p', {'class': 'now'}) is not None else None
            humidity = data.find('p', {'class': 'minmax'}).text if data.find('p', {'class': 'minmax'}) is not None else None
            wind = data.find('p', {'class': 'wind'}).text if data.find('p', {'class': 'wind'}) is not None else None
            weather_data.append({'City': city, 'Temperature': temp, 'Humidity': humidity, 'Wind': wind})
            data1 = data.find_next('div', {'class': 'capital'})
            data = data1
            i += 1
        else:
            data= data.find_next('div', {'class': 'capital'})
            i += 1
            print('Data not found')
   
    return jsonify(weather_data)

def get_image_from_google_drive(drive_url):
    try:
        # Extract the file ID from the Google Drive URL
        file_id = drive_url.split('/')[-2]
        if not file_id:
            print(f"Invalid URL: {drive_url}")
            return drive_url

        # Create the direct download URL
        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        
        # Send a GET request to the download URL
        response = requests.get(download_url)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Read the image data
            image_data = BytesIO(response.content)
            # Open the image using Pillow
            image = Image.open(image_data)
            return image
        else :
            return 1
    except IndexError:
        print(f"Failed to extract file ID from URL: {drive_url}")
        return None

def get_file_extension(url):
    response = requests.head(url)
    content_type = response.headers.get('content-type')
    if content_type:
        extension = mimetypes.guess_extension(content_type)
        return extension
    return '.jpg'

def download_jpg(url, file_path, file_name):
    file_extension = get_file_extension(url)
    full_path = file_path + file_name + file_extension
    print(f"Image saved to {full_path}")
    urllib.request.urlretrieve(url, full_path)

def download_image(url, save_path, file_name):
    image = get_image_from_google_drive(url)
    if image==1:
        download_jpg(url,save_path,file_name)
        return
        
    elif image:
        # Determine the correct file extension based on the image format
        file_extension = image.format.lower()
        if file_extension not in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
            print(f"Unsupported file format: {file_extension}")
            return
        
        # Append the correct extension to the file name
        file_path = os.path.join(save_path, f"{file_name}.{file_extension}")
        image.save(file_path)
        print(f"Image saved to {file_path}")
        return file_extension
    else:
         print(f"Failed to download image from {url}")


@app.route('/image_data')
def image_data():
    # get all the records of the data
    records_data = sheet_instance.get_all_records()
    #data.append({'City': city, 'Min': min_temp, 'Max': max_temp,'Marq':marquee,'High':Highest,'Low':Lowest})
    # view the data
    # Fetch and validate image URLs
    for record in records_data:
        if record['Url']:
            url = record['Url']
            file_name = record['UrlName']
            file_extension=download_image(url, r"", file_name) # set the folder to save the image link from Google Sheet
            if file_extension:
                file_extension="."+file_extension
            else:
                file_extension = get_file_extension(url)
            record['Extension']=file_extension
    # Return the data as JSON 
    return jsonify(records_data)

@app.route('/excel_data')
def excel_data():
    # get all the records of the data
    records_data = sheet_instance.get_all_records()
     #data.append({'City': city, 'Min': min_temp, 'Max': max_temp,'Marq':marquee,'High':Highest,'Low':Lowest})  
    return jsonify(records_data)

@app.route('/Sos_data')
def sos_data():
    records_data = sheet_instance.get_all_records()
    for record in records_data:
         if record['SosLink']:
            url = record['SosLink']
            file_name = record['SosName']
            file_extension=download_image(url, r"", file_name) # set the folder to save the image link of SOS from Google Sheet
            if file_extension:
                file_extension="."+file_extension
            else:
                file_extension = get_file_extension(url)
            record['SosExtension']=file_extension
                
    return jsonify(records_data)

if __name__ == '__main__':
    app.run(debug=True)
