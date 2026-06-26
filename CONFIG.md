## Channel Definitions
Spark can be configured to collect channel guide data from your desired sources with ease using a simple JSON configuration file. Take a look at [channels.example.conf](https://github.com/Mosenia-Cable/spark/blob/main/channels.example.conf) for reference. Each channel is configured as a dict object within the root list in the file. For example, here is what an individual channel looks like:
```json
{
    "num": 1,
    "type": "4broadcast",
    "endpoint": "https://4broadcast.yourdomain.tld",
    "target_id": "MyXmlTvChannelID"
}
```
### Properties
- **num**: The numerical identifier for the channel, representing the channel number that the station's broadcast can be viewed on. Sub-channels can be identified using a single point decimal (i.e: 1.2).
- **type**: The type of endpoint to collect the guide data from, with five possible string values: "4broadcast" for collecting from 4broadcast APIs, "ersatz" for collecting from ErsatzTV XMLTV files, "gracenote" for collecting via Gracenote's API, or "xmltv" for collecting from any web address which points to an XMLTV file *or* collecting from a local file path. It can also be set to "static" if you want to define a channel with a continuous 24-hour program.
- **endpoint**: The URL of the 4broadcast API endpoint to collect from. This is only used if **type** is "4broadcast" or "ersatz".
- **target_id**: The string of the desired channel ID to collect data from in the fetched XMLTV response. If left blank or null, Spark will use the first channel ID it finds in the XMLTV (helpful if you're using 4broadcast API, as only one channel should be present).
- **program**: Only used if **type** is "static". Holds a dict object which contains keys mapping the guide data as defined by you. See [channels.example.conf](https://github.com/Mosenia-Cable/spark/blob/main/channels.example.conf) for an example of what values you can define.

## Export Definitions
Spark can output the final OnCable delimited (.del) files wherever you specify. By default, it's ".export" in the program's local folder, but you can overwrite this by creating an export configuration file. See [export.example.conf](https://github.com/Mosenia-Cable/spark/blob/main/export.example.conf). The export config file is only probed for one value at this time, "dir", as the final destination for the delimited files.
```json
{
    "dir": "C:\\Zap2It\\OnCable\\EXPORT\\ZAP2IT"
}
```
### Properties
- **dir**: The folder path of which the composite .del files will be exported to.

## Weather
Zap2It supports displaying simple weather data and Spark is able to fulfill that thanks to WeatherAPI.com's free tier API. To acquire an API key, [create an account for free](https://www.weatherapi.com/signup.aspx). When you get to your dashboard, you should have an API key displayed that you can copy. Place this into **weatherapi.com-api-key** in your weather.conf file (see [weather.example.conf](https://github.com/Mosenia-Cable/spark/blob/main/weather.example.conf) for format example, or see below). To make sure you have all data fields available, visit "API Response Fields" to the left on your dashboard, and enable all optional fields (hit Save at the bottom!).
```json
{
    "headend": "ZAP2IT",
    "zipcode": "87901",
    "locname": "Truth or Consequences",
    "weatherapi.com-api-key": "your-api-key-goes-here"
}
```
### Properties
- **headend**: Headend ID used by Zap2It for identification. This must match your installation's headend ID, otherwise it will not display.
- **zipcode**: ZIP code of the desired location you want to collect weather data for. This could also be a coordinate pair.
- **locname**: String name of the location you want to display weather data for.
- **weatherapi.com-api-key**: Your WeatherAPI.com API key, as a string. You can't get weather data without this.