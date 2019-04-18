# Zero2API

## Overview

This repo considers fast (time scale ~ one hour) publication of tabular data together with an active API 
for data query/retrieval[.](https://github.com/robfatland/ops) 
[Here is a link](https://docs.google.com/presentation/d/1LVCK0Szvvyhhgzuvk1U19P8XL9qaAKOuDXEJcYeAVTA/edit?usp=sharing)
to a presentation on this topic from FOSS4G-NA 2019.


'On hour to publish' sounds nice but we'd like to not over-promise. 
To get the deployment time down in that one hour range: You will need to do some advance preparation
and also do some practice. This repo has three subfolders to treat as sequential walk-throughs `1_publish_table`, 
`2_build_api` and `3_create_client`.


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


* **Why?** Science advances when data availability is not an obstacle; but often it *is*. We built this open tool 
for data publication as a set of templates to overcome this obstacle. There are many additional motivations that 
touch on more specifics of data-driven research from writing good Data Management Plans -- and executing on them --
to supporting team collaboration to demonstrating data democratization to reproducibility. 
* **How?** We create a publication pattern built from real *need-driven* use cases. 
Our model for self-publishing datasets presumes domain expertise applied to the data; an informed
(but not dictatorial) frame of mind. The procedural depends in particulars on the AWS cloud technology stack;
but with an open design that would easily translate to other clouds. Three provided Python code templates
do the work where the second in the sequence, the API translator, requires the bulk of the effort. 
We also provide a test dataset and of course the procedural. From there it is a matter of messaging
availability and in the tradition of open source seeing how community trial and adoption goes.
* **What?** We prototype a system on the AWS public cloud with two culmination points. First the 
table access API returns simple query results (HTML or JSON). Second we build a *composition API* that 
delivers a higher-level derived results: Speed and dispersion for the group of individuals described
by the data table. The derived result API makes use of the table access API. We address sub-topics 
in passing including documentation, data security, API design, registration of the resource, 
complexity, cost, source citation, discovery and obsolescence. 


### Furthermore... the extended narrative


It can be tempting to try and build extensive customization into the access API. Our suggestion is to
make the access API as simple as possible.  This avoids anticipating future use and *does not prevent*
subsequently building other APIs. This brings us to *composition*: Once a dataset is emplaced we are 
free to write a second data service (and a third, and a fourth, ...) built upon the first and potentially 
making use of other resources. As an example consider predicting juvenile salmon survival rates in a
river. Such a service could be composed of (informed by) precipitation and stream gauge data, turbidity 
sensor data, water temperature records, bird counts, sport fishing catch reports, water chemistry 
field data and so on.


With all this in hand we now give a longer narrative of the procedure covered in sections 1, 2 and 3.


We begin with a tabular dataset (CSV file) that you are welcome to use for practice.
Here is a link to the 
[(back-story link)](https://en.wikipedia.org/wiki/Amboseli_Baboon_Research_Project) of this dataset.
The CSV file has 1048576 rows in four columns and includes a header row **`indiv, time, x, y`**. 
Each row is a GPS fix converted to meters relative to an arbitrary local reference origin. Fixes were recorded
every two seconds for 26 individuals within a larger *congress* of baboons over the course of one day.
The individual identifiers are 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 20, 
21, 23, 24, 25, 31, 33, 35 and 38.

- Set up an AWS account; select a working **region**, ensure DynamoDB is enabled in that region
- Your local machine: Install the `boto3` Python package (the AWS interface library)
- Your local machine: Clone this Zero2API repository. You may wish to re-name it to suit your project
  - *load.sh* is edited to reflect the dataset. 
    - It is run once with a 'credentials' argument to establish a safe cloud access path
    - It is run a second time with a `load_data` argument
      - by default this will publish the example *table.csv* data
      - a service URL is returned
      - the data are now resident on a cloud database service
      - A simple/trivial API is now active at the service URL


The above steps are the first half of the process. They require about an hour given our starting assumptions. 
This does not include the time required to prepare the data as a flat table nor the time to set up the cloud 
account with credentials. 

The second part of the process involves refining the data access interface or API (Application Programming Interface). 

- *api.py* is edited 
  - *load.sh* is run with a `push_api` argument to pushed the API code to the cloud
    - This supersedes the default/prior API code
- *client.ipynb* and/or *client.py* is modified and used to test the API
- These steps are iterated as needed


Once data provisioning and API development are complete the data service will incur a monthly cost. Suppose this 
is $10 per month and the objective is to maintain the data service for five years. The total cost of $600 might
grow depending on data download charges (ten cents per GB). A cost estimate and a pre-pay mechanism are needed 
and will be addressed in this proposed work. 


Note that once the publication of the data is complete the Researcher's modified repository -- particularly the 
*Client* code -- becomes the reference for the API, i.e. for anyone to create a data service Client. 
