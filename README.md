# translate-pdf
# Setup

**Download the GitHub repository**

`git clone https://github.com/ALKRIS-55/translate-pdf.git`

`cd translate-pdf`

**Install virtual environment**

`sudo apt install python3-venv -y`

**Create a virtual environment**

`python3 -m venv venv`

**Activate the virtual environment**

`source venv/bin/activate`

**Install the dependencies**

`pip install -r requirements.txt`

**Go to the fairseq directory and install the dependencies**

```bash
cd fairseq
pip install ./
pip install xformers
python3 setup.py build_ext --inplace
cd ..

# Add the fairseq folder to the PATH
echo 'export PYTHONPATH=$PYTHONPATH:/path/to/your/home/directory/fairseq/' >> ~/.bashrc
echo 'export PYTHONPATH=$PYTHONPATH:/path/to/your/home/directory/indicTrans/' >> ~/.bashrc
source ~/.bashrc

# Activate the virtual environment if it was deactivated from above code
source venv/bin/activate
```

### **Installing the model**

```bash
# Translation Model
wget https://ai4b-public-nlu-nlg.objectstore.e2enetworks.net/indic2en.zip
unzip indic2en.zip
# Detection Model
wget https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin
```

# **Testing**

> **FOR THE PDF_TRANSLATION**

**Go to indicTrans directory and run the pdf_translation_api.py**

```bash
cd indicTrans
uvicorn pdf_translation_api:app --reload

```

**Now open the postman**  

1. Make the method **POST** 
2. URL **`http://localhost:8000/translate_pdf`**
3. Go to **Body** section choose **form-data**
4. API takes 3 parameter so make 3 keys value pair 

| Key | Value |
| --- | --- |
| file | Choose the file from your system |
| vernacular_pages_num | Enter the number on which the language is not English. The page number should be separated by the commas. For eg. “2,3,5” |
| language | Specify the vernacular language. For eg. “Hindi”  |
5. Hit the **SEND** button

> **FOR JUST THE TRANSLATION OF THE TEXT**

**Go to indicTrans directory and run the pdf_translation_api.py**

```bash
cd indicTrans
uvicorn translation_api:app --reload

```

**Now open the postman**  

1. Make the method **POST** 
2. URL **`http://localhost:8000/translate_en`**
3. Go to **Body** section choose **raw**
4. API takes the JSON format

```json
{
    "text": "அவனுக்கு நம்மைப் தெரியும் என்று தோன்றுகிறது"
}
```
5. Hit the **SEND** button
