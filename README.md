# Zero2API

## Overview

This repo considers fast (time scale ~ one hour) publication of tabular data together with an active API 
for data query/retrieval[.](https://github.com/robfatland/ops)


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


* **Why?** Science advances when data availability is not an obstacle; but too often it *is* an obstacle. We see a need to publish, pay for and then 'forget about' datasets knowing they will be there for five years. We call this **data provisioning**. From Data Management Plans to team collaborations there are many incentives and many opportunities to make *small* *specialized* datasets easy to access via RESTful interface queries with no maintenance. 
* **How?** We create publication patterns built from real *need-driven* use cases. We distill away details the publishing Researcher does not need. The Researcher follows the pattern, tests the resulting access protocol (API), and gets on with their research. 
* **What?** We will prototype this system on the AWS and Google public clouds using simple datasets. We will address a number of sub-topics including documentation, data security, API design and composition, registration, complexity, cost, source citation, discovery and technology obsolescence. We will then rinse-and-repeat with more complicated datasets until the money runs out. 


### Is and Is Not


The goal here is rapid self-publication of a tabular dataset. Ultimately we would like a pay-in-advance model for the cloud
resources so that the published data are available for a specified time without any upkeep (if the underlying services 
are stable, a big *if* we admit).

This project integrates a few technology components -- 
particularly cloud services like serverless computing -- with some Python code to provide flexible implementation. 
This is not a comprehensive solution however. The data capacity is limited and there is very little anticipation of 
*large robust data system* behavior.

*It might be tempting to try and build a lot of customization
into the access API. Suggestion: Make the access API as simple as possible. 
This avoids anticipating future use (may be inaccurate) without prohibiting subsequent composition...*


A second aspect of this project is *composition*: Once a dataset is emplaced we are free to write a second data 
service (and third, fourth, ...) built upon the first and potentially on other resources. As an example consider a 
high-level task of predicting juvenile salmon survival rates. Such a service could be composed / synthesized from 
precipitation and stream gauge data, turbidity measurements, water temperature records, predator appraisals such as 
bird counts or sport fishing catch reports, and water chemistry field data. These may be from disparate data resources. 



### Extended Narrative

This needs a lot of updating...

We begin with a tabular dataset (CSV file)
[(back-story link)](https://en.wikipedia.org/wiki/Amboseli_Baboon_Research_Project)
of 1048576 rows and four columns including a header **`indiv, time, x, y`**. Each row is a GPS
fix in meters relative to an arbitrary reference. These were recordead every two seconds for 25 
individual baboons over the course of a day. Proceeding on AWS:

- Set up an AWS account; we will be using DynamoDB so that must be enabled
- On a local machine AWS API is installed (called the AWS *CLI* for Command Line Interface)
- On GitHub the Researcher clones the Zero2API repository and re-name it to suit the data
  - Herein are files: *requirements.txt*, *api.py*, *client.ipynb*, *client.py*, *README.md*, *load.sh*, *table.csv*
  - There are also two launch buttons: For **binder** and **colab**
  - There is some CI machinery...

- *README.md* renders as an instruction manual
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
