'''Use this script to automatically re-fetch guide and weather data in the background.'''
import main
import weather
import common
import time
import logging
log = logging.getLogger("Spark Background Loop")
LAST_WX_STAMP = 0
LAST_GUIDE_STAMP = 0
EXPIRE_GUIDE_INTERVAL = 1800 # half an hour
EXPIRE_WX_INTERVAL = 3600 # hourly
if __name__ == "__main__":
    import coloredlogs
    coloredlogs.install(level="INFO")
    while True:
        if time.time() > LAST_GUIDE_STAMP + EXPIRE_GUIDE_INTERVAL:
            log.info(f"Updating channel guide data...")
            try:
                main.run() # run main processing loop
                LAST_GUIDE_STAMP = time.time() # remember when we last collected the guide data
                log.info(f"Updated channel guide data!")
            except:
                log.error(f"main.py encountered an unhandled error!", exc_info=True)
        if time.time() > LAST_WX_STAMP + EXPIRE_GUIDE_INTERVAL:
            log.info("Updating weather data...")
            try:
                weather.run() # run weather processing loop
                LAST_WX_STAMP = time.time()
                log.info(f"Updated weather data!")
            except:
                log.error(f"weather.py encountered an unhandled error!", exc_info=True)
        time.sleep(60) # wait 60 seconds before checking if we need to run again.