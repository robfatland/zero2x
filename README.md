# Zero2API
## Zero To API Rapid Data Publication

### Motivation


* **Why?** From Data Management Plans to team collaborations: Science advances when data availability is not an obstacle. Too often: It *is* an obstacle. We see a need to publish, pay for and then 'forget about' datasets knowing they will be there for five years. 
* **How?** We create publication patterns built from real *need-driven* use cases. We distill away everything you don't need to know; all you do is follow the pattern, test your access protocol (API), and get on with your research. 
* **What?** We will prototype this system on the AWS and Google public clouds using simple datasets. We will address a number of sub-topics including data security, API design and composition, registration, complexity, cost, citation and discovery. We will then rinse-and-repeat with more complex datasets until the money runs out.


### High Level Narrative


Zero To API will bootstrap from practical use cases: Part of the work is a "Gather Use Cases" process. Let's begin 
with a tabular dataset with one million rows and four columns. The columns are **ID**, **x**, **y**, and **timestamp**. (This
is based upon real data: GPS tracks of 25 individual baboons over one day in the Amboseli ecosystem of East Africa.) We present here a narrative that indicates both 'what is happening' and 'what the Researcher needs to know'. 


The Researcher is assumed to have three assets: A dataset on a Linux machine, a cloud account or access to a cloud via brokerage, 
and an account on and familiarity with GitHub. 


- On GitHub the Researcher clones the Zero2API repository and re-name it to suit the data
  - Herein are files: *requirements.txt*, *api.py*, *client.ipynb*, *client.py*, *README.md*, *load.sh*, *table.csv*
  - There are also two launch buttons: For **binder** and **colab**
  - There is some CI machinery...

- *README.md* renders as an instruction manual
  - *load.sh* is edited to reflect the dataset and run with a `load_data` argument
    - by default this will publish the example *table.csv* data
    - credentials are entered, used and evaporated
    - a service URL is returned
    - the data are now resident on a cloud database service
    - the API is now active but only trivially functional: at the service URL
  - *api.py* is edited and pushed to the cloud (`push_api` argument) replacing the default API
  - *client.ipynb* is modified and used to test the API
  
The above process (which is not yet complete) requires about an hour given our assumptions. This does not include the 
time required to prepare the data as a flat table nor the time to set up the cloud account with credentials. 
It also does not assign the API service a human-friendly DNS entry. The basic procedure does not require the 
Researcher to know about the underlying cloud services. These include an API handler ('API Gateway' on AWS,
'fubar' on Google Cloud Platform), a serverless compute function ('AWS Lambda'/'Google Version') and a 
relational database service ('RDS', 'Big Query or Something').


The next step is to iteratively improve upon the Client/Server relationship by editing and testing both *api.py* 
and *client.ipynb*. Once complete the data are available and will incur a monthly cost. Suppose this is $10 per
month and the objective is to maintain the data service for five years. The total cost is therefore $600 plus
any added charges for data downloads. Both a pre-pay mechanism and a cost estimate are needed and will be addressed
in this proposed work. 


Note that once the publication of the data is complete the new (originally cloned) repository becomes the reference
for using the API, i.e. for creating a data service Client. There is no need to create a portal or any other web
machinery. Once the pre-pay is complete the data will simply be available with no further effort.
