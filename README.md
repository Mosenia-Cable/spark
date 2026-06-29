![Spark](logo.png)
# Spark - Modern data management for the Zap2it EPG
Simply put, Spark is the ultimate data delivery solution for your existing Zap2it EPG installation, designed to be as comfortable to configure to your liking as possible. With support for fetching from **Gracenote**, **ErsatzTV**, **4broadcast**, or **any standard XMLTV web/file** endpoints, you can pull guide data from just about anywhere! Need to inject a static channel with a fixed 24/7 program title? Not a problem! Spark can do that, no sweat. Weather data can also be delivered by Spark with a little bit of additional setup.
# Installation
Prerequisites: You'll need **Python 3.8.10 or greater**. It may work on versions prior to 3.8.10, but this is the ideal minimum.

First, clone the repository. Since Spark contains a submodule (zap2it-GuideScraping), you will need to clone with --recurse-submodules. Failing to do this will result in non-functional **gracenote** endpoint types.
```
git clone --recurse-submodules https://github.com/Mosenia-Cable/spark
```
Once you've cloned, go ahead and install the **requirements.txt** with pip.
```
pip install -r requirements.txt
```
Congratulations! That's it for installation. Now, begin with configuration!
# Configuration
Before you configure Spark, if you plan to use **Gracenote** to fetch listings, you need to create a [config file for **zap2it-GuideScraping**](https://github.com/daniel-widrick/zap2it-GuideScraping/blob/main/zap2itconfig.ini.dist). You'll need a **Gracenote TV Listings account**. A little bit of Google searching will lead you to where you need to be to create one.

Configuring Spark to collect channel data from your desired sources is simple and easy to do. In theory. [See **CONFIG.md**](https://github.com/Mosenia-Cable/spark/blob/main/CONFIG.md) for a full write-up on configuring each element of Spark.
- [Defining channels](https://github.com/Mosenia-Cable/spark/blob/main/CONFIG.md#channel-definitions)
- [Export paths](https://github.com/Mosenia-Cable/spark/blob/main/CONFIG.md#export-definitions)
- [Weather](https://github.com/Mosenia-Cable/spark/blob/main/CONFIG.md#weather)

The example.conf files will be loaded if a .conf file with the root name (i.e. "channels" or "export") is not found in the program directory. You have to create the .conf files, the example.conf files are there as a reference of how you can configure them.
# Running
There are two default ways to run Spark, but you are welcome to set it up to run however you please (system service, etc)! You can run **main.py** which will fetch your guide data based on the channels config and export to the defined directory in the export config, as a single-use run. 
```bash
python3 main.py
```
Or, you can run **loop.py** which will frequently auto-collect the channel guide and weather data based on the time intervals defined inside of the script. 
```bash
python3 loop.py
```
ADditionally, running **weather.py** manually will collect the weather data and export, as a single run.
# Special thanks
This project would not have been possible without the existing contributions of [**the XMLTV project**](https://github.com/xmltv/xmltv), [**zap2it-GuideScraping**](https://github.com/daniel-widrick/zap2it-GuideScraping/tree/main), and [**PajamaFrix**](https://github.com/PajamaFrix) + [his reverse-engineering of the OnCable Delimited guide data formats](https://park-city.club/~frix/oncable/delimited-schema.html). Please show some appreciation for all involved!