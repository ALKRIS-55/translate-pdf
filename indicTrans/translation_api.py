import fasttext
from fastapi import FastAPI, Form
from pydantic import BaseModel
from inference.engine import Model

app = FastAPI()

detection_model = '../lid.176.bin'
translation_model = Model(expdir='../indic-en')

# Language Dictionary
indic_language_dict = {
    'as': 'Assamese',
    'hi': 'Hindi',
    'mr': 'Marathi',
    'ta': 'Tamil',
    'bn': 'Bengali',
    'kn': 'Kannada',
    'or': 'Oriya',
    'te': 'Telugu',
    'gu': 'Gujarati',
    'ml': 'Malayalam',
    'pa': 'Punjabi',
    'en': 'English',
}

class Item(BaseModel):
    text : str
    
@app.post('/detect_language')
def get_language(text: Item):
    model = fasttext.load_model(detection_model)
    LANG = model.predict(text.text)
    language = LANG[0][0].split("__label__")[1]
    return language


@app.post('/translate_en')
def get_translation(text: Item):
    language = get_language(text)
    translation = translation_model.translate_paragraph(text.text, language,'en')
    return {"Language" : indic_language_dict[language],"Translation" : translation}

# @app.post('/translate_e')
# def get_translation(text: str = Form(...)):
#     language = get_language(text)
#     translation = translation_model.translate_paragraph(text, language,'en')
#     return {"Language" : indic_language_dict[language],"Translation" : translation}
    
    
# @app.post('/detect_languag')
# def get_language(text: str = Form(...)):
#     model = fasttext.load_model(detection_model)
#     LANG = model.predict(text)
#     language = LANG[0][0].split("__label__")[1]
#     return language