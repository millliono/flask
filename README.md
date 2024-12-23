* first time use:

flask --app washmaster init-db



* there after:

flask --app washmaster run --debug



### /
* availability (time remaining) from global variables
* user identification
* credits left (pricing info)
* washer OR dryer 
* activate for 1h 20m
* deacivate / cancel if you are the current user and clear variables



### /admin
* update db
* activate
* deactivate


#### activate
- check if power is available, otherwise do nothing and return error
- check if this user has enough credits
- enable power via api
- if above is successful, start timer
- decrease credits
- set global variables: username, timestamp

when timer ends:
- disable power via api
- if above is successful, clear global variables



--STATUS
curl -X POST https://shelly-149-eu.shelly.cloud/device/status -d "id=b0b21c10f7fc&auth_key=MmJmMDM4dWlk7FA603986E0FEE7CDEFE52E5F53A96EBCD7BC7196DF0856E6AE90EA4B9E3D68E57F97605E0C5028D"

--ON
curl -X POST https://shelly-149-eu.shelly.cloud/device/relay/control -d "channel=0&turn=on&id=b0b21c10f7fc&auth_key=MmJmMDM4dWlk7FA603986E0FEE7CDEFE52E5F53A96EBCD7BC7196DF0856E6AE90EA4B9E3D68E57F97605E0C5028D"

--OFF
curl -X POST https://shelly-149-eu.shelly.cloud/device/relay/control -d "channel=0&turn=off&id=b0b21c10f7fc&auth_key=MmJmMDM4dWlk7FA603986E0FEE7CDEFE52E5F53A96EBCD7BC7196DF0856E6AE90EA4B9E3D68E57F97605E0C5028D"