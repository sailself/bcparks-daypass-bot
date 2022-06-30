# BC Parks Day Use Pass Bot
Bot for getting Day Use Pass from BC Parks website

Currently it's just made for Joffre Lakes Provincial Park. But should be easy to extend to other parks too.
For captcha code, Azure speech recognition is better than the built in Google one. 
To get an Azure API key, sign up a free account and create a Speech service to get API key.

Remember to download the ffmpeg from here https://ffmpeg.org/download.html and put executable in the same folder.

Also you need to do 'pip install webdriver-manager selenium SpeechRecognition pydub azure-cognitiveservices-speech'
