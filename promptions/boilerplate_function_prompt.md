Given some function code snippets from a user, write the boilerplate code for user:
- Implement the function as wrapper function with signature: `<return type> <function name>(const char *buff, size_t bufflen, std::string &out)`
- Parse the input data as a JSON object using a third-party library called `IrisJson`, 
- Then extract the fields from the JSON object, call the original function using the extracted parameters
- If the function parameters is a struct, just respond the output as "Need Struct: <struct name>"
- The user need the precise output, if you are not sure the output, just respond the output as "NOT SURE"

Here's smoke examples:
## Input 1: with prmitive parameter type
```c++
virtual int joinChannel(const char* token, const char* channelId, const char* info,
                        uid_t uid) = 0;
```
## Output 1
```c++
int joinChannel(const char *buff, size_t bufflen,
                                   std::string &out) {
  TRY_CATCH_START
  std::string data(buff, bufflen);
  IrisJson reader = JSON_PARSE(data);

  string token = "";
  string channelId = "";
  string info = "";
  uid_t uid;
  if (!reader["token"].is_null()) token = reader["token"];
  if (!reader["channelId"].is_null()) channelId = reader["channelId"];
  if (!reader["info"].is_null()) info = reader["info"];
  if (!reader["uid"].is_null()) uid = (uid_t)(long) reader["uid"];

  IrisJson outdata;
  outdata["result"] = rtc_engine_->joinChannel(
      token.empty() ? nullptr : token.c_str(), channelId.c_str(),
      info.empty() ? nullptr : info.c_str(), uid);

  out = JSON_TO_STRING(outdata);
  TRY_CATCH_END
  return 0;
}
```

## Input 2: with a struct, but the structs not in the input
```c++
virtual int startLastmileProbeTest(const LastmileProbeConfig& config) = 0;
```
## Output 2
Need Struct: LastmileProbeConfig

## Input 3: with a struct, and the structs are in the input
```c++
struct LastmileProbeConfig {
  bool probeUplink;
  bool probeDownlink;
  unsigned int expectedUplinkBitrate;
  unsigned int expectedDownlinkBitrate;
};

virtual int startLastmileProbeTest(const LastmileProbeConfig& config) = 0;
```
## Output 3
```c++
int startLastmileProbeTest(const char *buff, size_t bufflen,
                                              std::string &out) {
  TRY_CATCH_START
  std::string data(buff, bufflen);
  IrisJson reader = JSON_PARSE(data);

  agora::rtc::LastmileProbeConfig config;

  IrisJson lastmileProbeConfigReader = reader["config"];

  if (!lastmileProbeConfigReader["probeUplink"].is_null())
      config.probeUplink = lastmileProbeConfigReader["probeUplink"];
    if (!lastmileProbeConfigReader["probeDownlink"].is_null())
      config.probeDownlink = lastmileProbeConfigReader["probeDownlink"];
    if (!lastmileProbeConfigReader["expectedUplinkBitrate"].is_null())
      config.expectedUplinkBitrate = lastmileProbeConfigReader["expectedUplinkBitrate"];
    if (!lastmileProbeConfigReader["expectedDownlinkBitrate"].is_null())
      config.expectedDownlinkBitrate = lastmileProbeConfigReader["expectedDownlinkBitrate"];

  IrisJson outdata;
  outdata["result"] = rtc_engine_->startLastmileProbeTest(config);

  out = JSON_TO_STRING(outdata);
  TRY_CATCH_END
  return 0;
}
```

