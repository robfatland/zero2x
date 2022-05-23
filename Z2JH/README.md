Let's have some fun building [Jupyter Hub infrastructure](https://zero-to-jupyterhub.readthedocs.io/en/latest/)
on Azure.



## The FAQ we would like to find (while learning this)

- If I am interrupted mid-stream: What becomes of my work?
    - Using the interactive cloud shell both file structure and cloud resources are present upon resuming from an interruption
- What is the care and feeding going to look like?
- What is the Z2JH the high-level breakdown?
    - Set up K8 (Kubernetes plus Helm)
    - Set up Jupyter Hub
    - Administrate
    - Resources
- What will this cost? 
- Should I do Littlest Jupyter Hub or this one?


## Notes from starting K8 on Azure

- from home base (z2jh) navigate to the [AKS instructions](https://zero-to-jupyterhub.readthedocs.io/en/latest/kubernetes/microsoft/step-zero-azure.html)
- choose to use the Azure interactive shell to use the `az` Azure command line.
- log in to portal.azure.com
- choose the correct subscription by un-checking a default blinder
- back up to Home (upper left) to verify Subscription
- select the interactive shell icon at upper right to start the interactive shell
- select bash 
- if obstacle on storage creation: open up Details and create a new Resource group etcetera
- Create Storage: used rob5z2jh01 (lower case only)
- Shell terminal opens but begins madly resizing... oh dear


```
az account list --refresh --output table
az account set --subscription 'etcetera'
az group create --name=rob5rgz2jh01 --location=westus2 --output table
mkdir rob5z2jh01
cd rob5z2jh01
ssh-keygen -f ssh-key-rob5z2jh01
```


At this point we have a named cluster and a key pair. We ignore the text printed in that last step, by the way.


Now for vnet + subnet

```
az network vnet create --resource-group rob5z2jh01 --name rob5z2jh01-vnet --address-prefixes 10.0.0.0/8 --subnet-name rob5z2jh01-subnet --subnet-prefix 10.240.0.0/16
```

Ignoring the JSON text flush; on to setting two ID variables.


```
VNET_ID=$(az network vnet show --resource-group rob5z2jh01 --name rob5z2jh01-vnet --query id --output tsv)
SUBNET_ID=$(az network vnet subnet show --resource-group rob5z2jh01 --vnet-name rob5z2jh01-vnet --name rob5z2jh01-subnet --query id --output tsv)
```

I now tried to execute this: 


```
SP_PASSWD=$(az ad sp create-for-rbac --name rob5z2jh01-sp --role Contributor --scopes rob5z2jh01-vnet --query password --output tsv)
```


However I received `ERROR: The request did not have a subscription or a valid tenant level resource provider.` The instructions 
indicate that I need Owner role for this to succeed; so that may be the issue. I look this up under Subscription > IAM and find 
that I am a Contributor, not an Owner. So that was a good start but it is time to up my ranking before trying again. 


With some hassles I realigned my User account with the Owner role (promoted from Contributor) and ran these two 'are they still there'
commands:

```
az group list --output table
az network vnet list --output table
```

`--output table` avoids having to stare at disgusting JSON content. My key files are still present in the subfolder
I made for this project in the interactive shell.










