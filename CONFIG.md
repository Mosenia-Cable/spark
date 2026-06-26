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
- **type**: The type of endpoint to collect the guide data from, with four possible string values: "4broadcast" for collecting from 4broadcast APIs, "ersatz" for collecting from ErsatzTV XMLTV files, or "gracenote" for collecting via Gracenote's API. It can also be set to "static" if you want to define a channel with a continuous 24-hour program.
- **endpoint**: The URL of the 4broadcast API endpoint to collect from. This is only used if **type** is "4broadcast" or "ersatz".
- **target_id**: The string of the desired channel ID to collect data from in the fetched XMLTV response. If left blank or null, Spark will use the first channel ID it finds in the XMLTV (helpful if you're using 4broadcast API, as only one channel should be present).
- **program**: Only used if **type** is "static". Holds a dict object which contains keys mapping the guide data as defined by you. See [channels.example.conf](https://github.com/Mosenia-Cable/spark/blob/main/channels.example.conf) for an example of what values you can define.
