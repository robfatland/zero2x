# Zero2API
## Zero To API Rapid Data Publication

Before UW proposal material let's review a couple key passages from the solicitation, first from NSF: 

> E-CAS will have two phases. The first phase will support six different scientific and engineering applications and workflows with cloud computing allocations and resources for development and code migration. After identifying two final projects selected from the original six, the second phase will commence for another year with a focus on delivering scientific results.


Then from Internet-2 bullets

* I2 + AWS + GCP; two phases as 6 Phase I --> 2 Phase II
* Two categories: Time-to-science and innovation 
* The project is guided by an external advisory board 
* Towards a new model of scalable cloud service partnerships to enhance science in a broad spectrum of disciplines. 
* $81k Total ask for Phase 1 with up to $100k cloud credits additional available


And from the lead paragraph some quotes: 


* growing academic / research computing and computational science communities
* illustrate the viability of these services as an option for leading-edge research across a broad scope of science. 
* simulation and application workflows such as those [on] HPC
* real-time analytics, artificial intelligence, machine learning, accelerated processing hardware, automation in deployment and scaling, and **management of serverless applications in order to provide digital research platforms to a wider range of science.** 
* [identify gaps in cloud provider stacks] which in contrast we identify a different sort of gap here...




### Motivation


* **Why?** Science advances when data availability is not an obstacle; but too often it *is* an obstacle. We see a need to publish, pay for and then 'forget about' datasets knowing they will be there for five years. We call this **data provisioning**. From Data Management Plans to team collaborations there are many incentives and many opportunities to make *small* *specialized* datasets easy to access via RESTful interface queries with no maintenance. 
* **How?** We create publication patterns built from real *need-driven* use cases. We distill away details the publishing Researcher does not need. The Researcher follows the pattern, tests the resulting access protocol (API), and gets on with their research. 
* **What?** We will prototype this system on the AWS and Google public clouds using simple datasets. We will address a number of sub-topics including documentation, data security, API design and composition, registration, complexity, cost, source citation, discovery and technology obsolescence. We will then rinse-and-repeat with more complicated datasets until the money runs out. 


### Is and Is Not


This project *is* an integration of technology components -- particularly cloud services like serverless computing -- with some
basic functional code to establish a baseline for fast self-publication. It is not an attempt to be a comprehensive solution; nor
is it intended as a data system with many moving parts (e.g. internal calibration and validation). This proposed work is an open source project starting point for further development by the open source community. 

This project is also in a philosophical sense modular or *compositional*.
By this we mean that once a dataset has been provisioned and given a simple access protocol a second data service 
can be composed using the first data service as its data source; and so on. As an example consider a high-level task
of predicting juvenile salmon survival rates. Such a service could be composed / synthesized from precipitation and 
stream gauge data, turbidity measurements, water temperature records, predator appraisals such as bird counts or 
sport fishing catch reports, and water chemistry field data; all from disparate sources. The implication of fire-and-forget
data services is that data are available while overhead costs (particularly time and effort) are largely gone. 


### Narrative


Zero To API will bootstrap from practical use cases: Part of the work is a "Gather Use Cases" process. Let's begin 
with a tabular dataset with one million rows and four columns. The columns are **ID**, **x**, **y**, and **timestamp**. (This
is based upon real data: GPS tracks of 25 individual baboons over one day in the Amboseli ecosystem of East Africa.) We present here a narrative that indicates both 'what is happening' and 'what the Researcher needs to know'. 


The Researcher is assumed to have three assets: A dataset on a Linux machine, a cloud account or access to a cloud via brokerage, 
and an account on and familiarity with GitHub. This person does not need to know about underlying technologies, for example
communication protocols, serverless computing, database management, HTTP verbs or cloud configuration languages like 
AWS CloudFormation. 


- On the local Linux machine the appropriate cloud API is installed (on AWS the *CLI*; on Google who knows)

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
grow depending on data download charges. A cost estimate and a pre-pay mechanism are needed and will be addressed
in this proposed work. 


Note that once the publication of the data is complete the Researcher's modified repository -- particularly the 
*Clien* code -- becomes the reference for the API, i.e. for anyone to create a data service Client. There is no 
need to create a portal or any other web machinery. Once the pre-pay provisioning is complete the data will simply 
be available with no further effort.
