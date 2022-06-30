#!/usr/bin/python3

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from pydub import AudioSegment
import azure.cognitiveservices.speech as azurespeech
import time
import speech_recognition as sr
import requests
import base64
import re as regex
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
conf = config['General']
pass_date = conf['date']
pass_count = conf['count']
first_name = conf['first_name']
last_name = conf['last_name']
email = conf['email']
azure_key = conf['azure_key']

def recognize_from_azure(audio_file):
    speech_config = azurespeech.SpeechConfig(subscription=azure_key, region="westus")
    speech_config.speech_recognition_language="en-US"

    audio_config = azurespeech.audio.AudioConfig(filename=audio_file)
    speech_recognizer = azurespeech.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    speech_recognition_result = speech_recognizer.recognize_once_async().get()

    if speech_recognition_result.reason == azurespeech.ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(speech_recognition_result.text))
        return speech_recognition_result.text
    elif speech_recognition_result.reason == azurespeech.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
    elif speech_recognition_result.reason == azurespeech.ResultReason.Canceled:
        cancellation_details = speech_recognition_result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == azurespeech.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
            print("Did you set the speech resource key and region values?")
    return null


if __name__ == '__main__':
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    # driver.maximize_window()
    driver.get("https://reserve.bcparks.ca/dayuse/registration")
    time.sleep(2)
    button = driver.find_element_by_css_selector("[aria-label='Book a pass for Joffre Lakes Provincial Park']")
    time.sleep(2)
    try: 
        button.click()
    except Exception as e:
        print(e)
        print("Button not clickable, try again...")
        button.click()
    time.sleep(2)
    date_input = driver.find_element_by_name('ngbDatepicker')
    date_input.clear()
    date_input.send_keys(pass_date)
    time.sleep(0.3)
    type_dropdown = Select(driver.find_element_by_id('passType'))
    type_dropdown.select_by_value('1: Object')
    time.sleep(0.3)
    time_input = driver.find_element_by_id('visitTimeDAY')
    time_input.click()
    time.sleep(0.3)
    passcount_dropdown = Select(driver.find_element_by_id('passCount'))
    passcount_dropdown.select_by_value(pass_count)
    time.sleep(0.3)
    next_button = driver.find_element_by_css_selector("[class='btn btn-primary']")
    next_button.click()
    time.sleep(1)
    fname_input = driver.find_element_by_id('firstName')
    fname_input.send_keys(first_name)
    lname_input = driver.find_element_by_id('lastName')
    lname_input.send_keys(last_name)
    email_input = driver.find_element_by_id('email')
    email_input.send_keys(email)
    agreement_checkbox = driver.find_element_by_xpath("//label[contains(text(),'I have read and agree to the above notice')]/input")
    agreement_checkbox.click()

    # Config pydub for converting mp3 to wav
    # https://stackoverflow.com/questions/55669182/how-to-fix-filenotfounderror-winerror-2-the-system-cannot-find-the-file-speci
    AudioSegment.ffmpeg = 'ffmpeg.exe'
    AudioSegment.converter = 'ffmpeg.exe'
    AudioSegment.ffprobe = 'ffprobe.exe'

    captcha_valid = len(driver.find_elements_by_class_name('captcha-valid'))
    old_audio_src_len = len(driver.find_element_by_tag_name('audio').get_attribute('src'))
    while captcha_valid < 1:
        while len(driver.find_elements_by_xpath("//*[text()='Play Audio']")) < 1:
            time.sleep(1)
        play_audio = driver.find_element_by_xpath("//*[text()='Play Audio']").find_element_by_xpath('..')
        play_audio.click()
        new_audio_src_len = len(driver.find_element_by_tag_name('audio').get_attribute('src'))
        while new_audio_src_len < 200 or new_audio_src_len == old_audio_src_len:
            time.sleep(1)
            new_audio_src_len = len(driver.find_element_by_tag_name('audio').get_attribute('src'))

        # Get audio from website and save it to mp3 file
        old_audio_src_len = len(driver.find_element_by_tag_name('audio').get_attribute('src'))
        audio_byte = base64.b64decode(driver.find_element_by_tag_name('audio').get_attribute('src').replace('data:audio/mp3;base64,', '', 1))
        mp3_filename = 'captcha.mp3'
        with open(mp3_filename, 'wb') as f: 
            f.write(audio_byte)
        time.sleep(1)
        # Convert mp3 to wav
        MP3_FILE = (mp3_filename)
        wav_filename = 'captcha.wav'
        sound = AudioSegment.from_mp3(MP3_FILE)
        sound.export(wav_filename, format="wav")
        # Use Google speach recognizer to convert audio to text
        WAV_FILE = (wav_filename)
        recognizer = sr.Recognizer()
        with sr.AudioFile(WAV_FILE) as source:
            audio = recognizer.record(source)
        audio2text = recognizer.recognize_google(audio)+''
        captcha_text = regex.sub('[^A-Za-z0-9]+', '', audio2text.lower()).replace('pleasetypeinfollowinglettersornumbers', '')
        print("######### Google speech2text: " + captcha_text)
        answer_input = driver.find_element_by_id('answer')
        answer_input.clear()
        answer_input.send_keys(captcha_text)
        time.sleep(0.5)
        captcha_valid = len(driver.find_elements_by_class_name('captcha-valid'))
        if captcha_valid == 1:
            break
        # Use Azure speach recognizer to convert audio to text
        audio2text = recognize_from_azure(WAV_FILE)
        captcha_text = regex.sub('[^A-Za-z0-9]+', '', audio2text.lower()).replace('pleasetypeinfollowinglettersornumbers', '')
        print("######### Azure speech2text: " + captcha_text)
        answer_input = driver.find_element_by_id('answer')
        answer_input.clear()
        answer_input.send_keys(captcha_text)
        time.sleep(0.5)
        captcha_valid = len(driver.find_elements_by_class_name('captcha-valid'))
        if captcha_valid < 1:
            new_image = driver.find_element_by_xpath("//*[text()='Try New Image']").find_element_by_xpath('..')
            new_image.click()


    submit_button = driver.find_element_by_xpath("//*[text()='Submit']").find_element_by_xpath('..')
    if submit_button.is_enabled():
        submit_button.click()
    else:
        time.sleep(2)
        submit_button.click()

    time.sleep(10)
