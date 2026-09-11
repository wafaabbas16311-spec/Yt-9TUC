import time
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# --- CONFIGURATION ---
VIDEO_URL = "https://youtu.be/GaHmkV-Lcx8"  # Replace with your URL
TARGET_HOURS = 100
NUM_INSTANCES = 5  # Number of parallel browser instances
TOTAL_SECONDS_NEEDED = TARGET_HOURS * 3600

def create_driver():
    """Create and configure Chrome driver for Railway"""
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
            video.playbackRate = 2.0;  // Play at 2x speed for faster watch time
        """)
        
        # Click play button if present
        try:
            play_button = driver.find_element(By.CLASS_NAME, "ytp-large-play-button")
            play_button.click()
        except:
            pass
        
        start_time = time.time()
        elapsed = 0
        
        while not stop_event.is_set() and elapsed < TOTAL_SECONDS_NEEDED:
            time.sleep(60)  # Check every minute
            elapsed = time.time() - start_time
            
            # Check if video is still playing
            try:
                is_playing = driver.execute_script("return !document.querySelector('video').paused")
                if not is_playing:
                    # Try to replay the video
                    driver.execute_script("""
                        var video = document.querySelector('video');
                        video.currentTime = 0;
                        video.play();
                    """)
            except:
                pass
            
            # Refresh every 25 minutes to count as new view
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
    print(f"Target: {TARGET_HOURS} hours ({TOTAL_SECONDS_NEEDED} seconds)")
    print(f"With {NUM_INSTANCES} instances at 2x speed, estimated time: {TOTAL_SECONDS_NEEDED/(NUM_INSTANCES*2)/3600:.1f} hours")
    
    stop_event = threading.Event()
    threads = []
    
    # Start multiple instances
    for i in range(NUM_INSTANCES):
        thread = threading.Thread(target=watch_video, args=(i+1, stop_event))
        thread.start()
        threads.append(thread)
        time.sleep(5)  # Stagger start to avoid overload
    
    # Monitor progress
    try:
        while True:
            time.sleep(60)
            print(f"Running... {len([t for t in threads if t.is_alive()])}/{NUM_INSTANCES} instances active")
    except KeyboardInterrupt:
        print("\nStopping all instances...")
        stop_event.set()
        
        # Wait for threads to finish
        for thread in threads:
            thread.join(timeout=10)
        
        print("All instances stopped.")

if __name__ == "__main__":
    main()
    
