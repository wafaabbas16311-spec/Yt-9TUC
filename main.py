import os
import time
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# --- CONFIGURATION (from environment variables) ---
VIDEO_URL = os.getenv("VIDEO_URL", "https://youtube.com/shorts/GaHmkV-Lcx8?si=uIFsk06BJ1bdMdqd")
TARGET_HOURS = int(os.getenv("TARGET_HOURS", "100"))
NUM_INSTANCES = int(os.getenv("NUM_INSTANCES", "3"))  # Reduced for GitHub Actions
TOTAL_SECONDS_NEEDED = TARGET_HOURS * 3600

def create_driver():
    """Create and configure Chrome driver"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--mute-audio")
    chrome_options.add_argument("--autoplay-policy=no-user-gesture-required")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def watch_video(instance_id, stop_event):
    """Watch video in a loop until stop_event is set"""
    print(f"Instance {instance_id}: Starting...")
    
    try:
        driver = create_driver()
        driver.get(VIDEO_URL)
        
        # Wait for video to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "video"))
        )
        
        # Mute video and set playback rate
        driver.execute_script("""
            var video = document.querySelector('video');
            video.muted = true;
            video.playbackRate = 2.0;
        """)
        
        # Click play button if present
        try:
            play_button = driver.find_element(By.CLASS_NAME, "ytp-large-play-button")
            play_button.click()
        except:
            pass
        
        start_time = time.time()
        elapsed = 0
        
        # Run for 6 hours (GitHub Actions limit)
        max_runtime = 6 * 3600  # 6 hours in seconds
        
        while not stop_event.is_set() and elapsed
        
