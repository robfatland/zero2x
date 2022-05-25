Let's have some fun building [Jupyter Hub infrastructure](https://zero-to-jupyterhub.readthedocs.io/en/latest/)
on Azure.



## The FAQ we would like to find (while learning this)

- Any supporting links?
    - [The Naomi Formulation](https://curious-poppyseed-2cf.notion.site/Zero-To-Jupyterhub-Script-83866ee697964443a579d5b3f2500e4b)
    - Original [ZeroToJupyterHub site](https://zero-to-jupyterhub.readthedocs.io/en/latest/) (can become outdated in some details)
    - An FAQ on the [Azure Kubernetes Service (AKS)](https://docs.microsoft.com/en-us/azure/aks/faq) for orchestrating containers
    - [This page](https://github.com/robfatland/zero2x/edit/master/Z2JH/README.md)
- As we proceed with creating many Azure resources: Good naming scheme?
    - choose a short base string (I use `r5`)
    - For each resource: Add a hyphen and two-character identifier
    - Example: A resource group and a service principal are respectively `r5-rg` and `r5-sp`
        - (A service principal is an automaton)
- If I am interrupted mid-process: What becomes of my work?
    - I used the interactive cloud shell 
    - file system modifications were intact (e.g. key pair files) 
    - cloud resources (RG, vnet, subnet) were still present
    - environment variable assignments were lost
    - commands to recreate them are still available in `history`
- What is the care and feeding going to look like?
    - Part One: What is the complete "box of toys" including those generated automatically / invisibly
    - Part Two: What is likely to break or need attention in one / three / six / twelve / 24 months?
    - Part Three: How do we respond when the team wants to install additional...?
        - Python modules (and how do ***environments*** factor in?)
        - Software, from MATLAB to Tableau
- What is the Z2JH the high-level breakdown?
    - Set up K8 (Kubernetes plus Helm)
        - Why should I fear the phrase `RequestDisallowedByPolicy`?
    - Set up Jupyter Hub
    - Administrate
    - Resources
- What will this cost? 
- Should I do Littlest Jupyter Hub or this one?


## Notes from following K8 on Azure

- Navigate to the Z2JH [AKS instructions](https://zero-to-jupyterhub.readthedocs.io/en/latest/kubernetes/microsoft/step-zero-azure.html)
- Login to [Azure](https://portal.azure.com)
- Choose the correct subscription (filter can obscure this) and verify that's where you are
- Click the Azure interactive shell icon (upper right) to facilitate using the `az` Azure command line.
    - Use **Advanced Settings** to create a new Resource Group etc under the correct subscription; be sure to select `bash` 
    - I will use `r5-rg`, `r5sa`, `r5-fs` for resource group, storage account and file share. '-' not permitted in storage account names, forsooth. 
- Shell terminal opens but begins madly resizing... oh dear


```
az account list --refresh --output table
az account set --subscription 'rob5 teaching'
az account list --refresh --output table
```

This should show `True` under `Is Default` for the subscription we choose.


Suppose that in starting up the interactive shell we created a resource group. Then we do not need to do that now. 
On the other hand if we did *not* then *now* is the time to do it; with a name that is aligned with this project.


```
az group create --name=r5-rg --location=westus --output table
```


Next let's make a directory with a familiar name, go there, and create an ssh key pair.


```
mkdir r5
cd r5
ssh-keygen -f ssh-key-r5
ls -al
```


Ignore the text printed in the last step; it will not come in to play.
Notice that `r5` label in the `ssh-keygen` command: That will be the cluster name.


Now for a virtual network `vnet` and within that a `subnet`. 
Use an editor (ctrl-x ctrl-e to open; or use vi) to create a multi-line command.


```
az network vnet create \
   --resource-group r5-rg \
   --name r5-vnet \
   --address-prefixes 10.0.0.0/8 \
   --subnet-name r5-subnet \
   --subnet-prefix 10.240.0.0/16
```


I call this file `next01` and run it with `source next01`. It takes a minute and dumps some JSON if it works.


Onwards to setting some variables.


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

This completed with four WARNING messages including one about 'credentials that you must protect'. These credentials are
the value of the `SP_PASSWD` variable (I presume).


To see details of this Service Principal (sp) we have

```
az ad sp list --show-mine
```

This produces a block of JSON. Copy out the servicePrincipalNames string: `88888888-4444-4444-4444-121212121212` 
for use setting the `SP_ID` variable below. I will refer to these as 844412 strings.


I left and came back later, using these commands to ensure the resources were still in place: 


```
az group list --output table
az network vnet list --output table
```

`--output table` avoids having to stare at too much JSON. My key files are still present in the subfolder
I made for this project in the interactive shell. I did re-run the `VNET_ID` and `SUBNET_ID` alias commands out of
history. 


Next: 


```
SP_ID=$(az ad sp show --id aaaaaaaa-d2d2-4848-9876-b6a7a7a7a7a7 --query appId --output tsv)
```


This is very unclear: I think the idea is to load in the 844412 string using this `az ad sp` command 
for the Service Principal but I just pulled it from the JSON earlier. 


Now to bring it all together and create the Azure kubernetes service (AKS) cluster.


```
az aks create --name rob5z2jh01-aks-cluster --resource-group rob5z2jh01 --ssh-key-value ssh-key-rob5z2jh01.pub \
   --node-count 3 --node-vm-size Standard_D2s_v3 --service-principal $SP_ID --client-secret $SP_PASSWD         \
   --dns-service-ip 10.0.0.10 --docker-bridge-address 172.17.0.1/16 --network-plugin azure                     \
   --network-policy azure --service-cidr 10.0.0.0/16 --vnet-subnet-id $SUBNET_ID --output table
```

...and I get a lot of red ink including the phrase `RequestDisallowedByPolicy`. 


To make sense of this and fix it we refer to the "process so far". We created a resource group that 
we find [from this faq](https://docs.microsoft.com/en-us/azure/aks/faq) is one of two needed. This
first RG. It contains the Kubernetes service resource. 


The second RG is created automatically and has a name assigned by default of the form 
`MC_myResourceGroup_myAKSCluster_westus2`. 
