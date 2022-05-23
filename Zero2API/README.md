# Overview

Fast (time scale ~ one hour) data publication plus an access API.
[Presentation: Start here.](https://docs.google.com/presentation/d/1LVCK0Szvvyhhgzuvk1U19P8XL9qaAKOuDXEJcYeAVTA/edit?usp=sharing)
(from FOSS4G-NA 2019)


Advance prep / reps needed. Proceed in 3 steps:

- 1_publish_table 
- 2_build_api
- 3_create_client


### Quick procedural summary

- publish the table
  - Secure and configure a cloud account (working example uses AWS)
  - Organize a `.csv` tabular data file to publish
  - Push the data into a cloud database-as-a-service (AWS DynamoDB table)
- build an application programming interface (API)
  - Associate a serverless API service (AWS Lambda with API Gateway)
  - Attach a stable URL to this service (AWS Elastic IP)
- write and test a `client` of the service


## Motivation


* **Why?** Model open data publication and access. 
* **How?** The procedural depends on particulars of a cloud technology stack (AWS, GCP, Azure etc)
There are three Python code templates; where the API translator is the effort. 
* **What?** Table access API returns simple query results (HTML or JSON). *Composition API* for 
higher-level derived results. In passing: documentation, data security, API design, 
complexity, cost, source citation, discovery and obsolescence. 


### Furthermore... the extended narrative


It can be tempting to build extensive customization into an access API. Our suggestion is to
make the access API as simple as possible.  This avoids anticipating future use and *does not prevent*
subsequently building other APIs. This is *composition*. Example: Predict juvenile salmon 
survival rates in a
river from precipitation and stream gauge data, turbidity 
sensor data, water temperature records, bird counts, sport fishing catch reports, water chemistry 
field data and so on. 


### Tabular dataset (CSV file)


[Back-story](https://en.wikipedia.org/wiki/Amboseli_Baboon_Research_Project)


The CSV file has 1048576 rows in four columns and includes a header row **`indiv, time, x, y`**. 
Each row is a GPS fix converted to meters relative to an arbitrary local reference origin. Fixes were recorded
every two seconds for 26 individuals within a larger *congress* of baboons over the course of one day.
The individual identifiers are 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 20, 
21, 23, 24, 25, 31, 33, 35 and 38.


- Set up an AWS account; select a working **region**, ensure DynamoDB is enabled in that region
- In DynamoDB set up an appropriate table; and note the endpoint URL
- Your local machine: Install the `boto3` Python package (the AWS interface library)
- Use `DynamoDB_load.py` to push the data to the DynamoDB table


The above steps are the first 'third' of the process. They require about an hour given our starting assumptions. 
This does not include the time required to prepare the data as a flat table nor the time to set up the cloud 
account with credentials. 

The second part of the process involves refining the data access interface or API (Application Programming Interface). 


Once data provisioning and API development are complete the data service will incur a monthly cost. 
Our estimate is $5 (USD) per month or $300 for five years. Once the dataset is published a GitHub 
repo is one obvious means to provide the API reference. Calling the API with no arguments might 
return a reference to this repo (or a docstring if that will suffice). 
