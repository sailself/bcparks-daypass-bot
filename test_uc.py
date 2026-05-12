import undetected_chromedriver as uc
import time

print("Starting UC...")
driver = uc.Chrome(version_main=147)
print("UC started.")
driver.get("https://www.google.com")
print("Page loaded: ", driver.title)
time.sleep(5)
driver.quit()
print("Done.")
