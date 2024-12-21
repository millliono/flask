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
