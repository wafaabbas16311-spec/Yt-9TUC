import os
import time
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURATION ---
VIDEO_URL = os.getenv("VIDEO_URL", "https://youtube.com/shorts/GaHmkV-Lcx8?si=SDTCq_kxz45qLcsH")
TARGET_HOURS = int(os.getenv("TARGET_HOURS", "100"))
NUM_INSTANCES = int(os.getenv("NUM_INSTANCES", "3"))
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
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Use Selenium Manager (no need for webdriver-manager)
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def watch_video(instance_id, stop_event):
    """Watch video in a loop until stop_event is set"""
    print(f"Instance {instance_id}: Starting...")
    
    try:
        driver = create_driver()
        driver.get(VIDEO_URL)
        
        # Wait for video to load
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "video"))
        )
        
        # Mute video and set playback rate
        driver.execute_script("""
            var video = document.querySelector('video');
            video.muted = true;
            video.playbackRate = 2.0;
            video.play();
        """)
        
        # Click play button if present
        try:
            play_button = driver.find_element(By.CLASS_NAME, "ytp-large-play-button")
            play_button.click()
        except:
            pass
        
        start_time = time.time()
        elapsed = 0
        
        # Run for 5 hours (GitHub Actions limit)
        max_runtime = 5 * 3600
        
        while not stop_event.is_set() and elapsed < min(TOTAL_SECONDS_NEEDED, max_runtime):
            time.sleep(60)
            elapsed = time.time() - start_time
            
            # Check if video is still playing
            try:
                is_playing = driver.execute_script("return !document.querySelector('video').paused")
                if not is_playing:
                    driver.execute_script("""
                        var video = document.querySelector('video');
                        video.currentTime = 0;
                        video.play();
                    """)
            except:
                pass
            
            # Refresh every 25 minutes
            if int(elapsed) % 1500 == 0:
                driver.refresh()
                time.sleep(5)
                driver.execute_script("""
                    var video = document.querySelector('video');
                    video.muted = true;
                    video.playbackRate = 2.0;
                    video.play();
                """)
                print(f"Instance {instance_id}: Refreshed at {int(elapsed/60)} minutes")
        
        print(f"Instance {instance_id}: Completed {elapsed/3600:.2f} hours")
        driver.quit()
        
    except Exception as e:
        print(f"Instance {instance_id}: Error - {str(e)}")

def main():
    print(f"Starting YouTube watch time bot with {NUM_INSTANCES} instances...")
    print(f"Target: {TARGET_HOURS} hours")
    print(f"Running for 5 hours (GitHub Actions limit)")
    
    stop_event = threading.Event()
    threads = []
    
    # Start multiple instances
    for i in range(NUM_INSTANCES):
        thread = threading.Thread(target=watch_video, args=(i+1, stop_event))
        thread.start()
        threads.append(thread)
        time.sleep(5)
    
    # Monitor progress
    try:
        while True:
            time.sleep(60)
            active = len([t for t in threads if t.is_alive()])
            print(f"Running... {active}/{NUM_INSTANCES} instances active")
            if active == 0:
                break
    except KeyboardInterrupt:
        print("\nStopping all instances...")
        stop_event.set()
        
        for thread in threads:
            thread.join(timeout=10)
        
        print("All instances stopped.")

if __name__ == "__main__":
    main()
    
