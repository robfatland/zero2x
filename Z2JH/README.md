Let's have some fun building [Jupyter Hub infrastructure](https://zero-to-jupyterhub.readthedocs.io/en/latest/)
on Azure.



## The FAQ we would like to find (while learning this)

- If I am interrupted mid-process: What becomes of my work?
    - I used the interactive cloud shell 
    - file system modifications were intact (e.g. key pair files) 
    - cloud resources (RG, vnet, subnet) were still present
    - environment variable assignments were lost
    - commands to recreate them are still available in `history`
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

In both of these cases we set the variable `XXX_ID` to the output of the az command. For example `echo $SUBNET_ID` produces


```
/subscriptions/c8c8c8c8-0a0a-4a4a-baba-7c7c7c7c7c7c/resourceGroups/rob5z2jh01/providers/Microsoft.Network/virtualNetworks/rob5z2jh01-vnet/subnets/rob5z2jh01-subnet
```

I now ensured my IAM Role was Owner and ran: 


```
SP_PASSWD=$(az ad sp create-for-rbac --name rob5z2jh01-sp --role Contributor --scopes $VNET_ID --query password --output tsv) 
```

This completed with four WARNING messages including one about 'credentials that you must protect'.

I left and came back later, using these commands to ensure the resources were still in place: 


```
az group list --output table
az network vnet list --output table
```

`--output table` avoids having to stare at disgusting JSON content. My key files are still present in the subfolder
I made for this project in the interactive shell. I did re-run the `VNET_ID` and `SUBNET_ID` alias commands out of
history. 










