Let's have some fun on Azure.

## FAQ

- If I am interrupted mid-stream: What becomes of my work?
- What is the care and feeding going to look like?
- What is the Z2JH the high-level breakdown?
    - Set up K8 (Kubernetes plus Helm)
    - Set up Jupyter Hub
    - Administrate
    - Resources
- What will this cost? 
- Should I do Littlest Jupyter Hub or this one?


## Notes from starting K8 on Azure

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












