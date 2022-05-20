# Zero2x

Notes on building CI from scratch

## Zero2JupyterHub


Let's sort out how this goes on Azure. [Instructions](https://zero-to-jupyterhub.readthedocs.io/en/latest/)


## Zero2API


### Overview

This repo considers fast (time scale ~ one hour) publication of tabular data together with an active API 
for data query/retrieval.
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
- In DynamoDB set up an appropriate table; and note the endpoint URL
- Your local machine: Install the `boto3` Python package (the AWS interface library)
- Use `DynamoDB_load.py` to push the data to the DynamoDB table


The above steps are the first 'third' of the process. They require about an hour given our starting assumptions. 
This does not include the time required to prepare the data as a flat table nor the time to set up the cloud 
account with credentials. 

The second part of the process involves refining the data access interface or API (Application Programming Interface). 

- couple details needed flag


Once data provisioning and API development are complete the data service will incur a monthly cost. 
Our estimate is $5 (USD) per month or $300 for five years. Once the dataset is published a GitHub 
repo is one obvious means to provide the API reference. Calling the API with no arguments might 
return a reference to this repo (or a docstring if that will suffice). 
