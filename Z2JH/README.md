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
It creates both a VNET and a SUBNET.


Once we have resources we should be able to list them. However this often involves some heirarchy.
Here we recover the names of both the vnet and the subnet just created:


```
az network vnet list --output table
az network vnet subnet list --resource-group r5-rg --vnet-name r5-vnet --output table
```


Onwards to setting some variables: This uses the output of an `az` command to set the `_ID` variables.


```
VNET_ID=$(az network vnet show \
   --resource-group r5-rg \
   --name r5-vnet \
   --query id \
   --output tsv)
SUBNET_ID=$(az network vnet subnet show \
   --resource-group r5-rg \
   --vnet-name r5-vnet \
   --name r5-subnet  \
   --query id \
   --output tsv)
```


`echo $VAR_NAME` demonstrates that we got it right.


Next: Create a 'Service Principal' (an agent who operates on Azure) using Active Directory.


```
az ad sp create-for-rbac \
   --name r5-sp \
   --role Contributor \
   --scopes $VNET_ID
```


This gives four key-value pairs including an ID and a PASSWD; so by copy-paste I manually set these:


```
SP_ID=<paste value>
SP_PASSWD=<paste value>
```

I echoed these values into a file called `next05.sp-info` so that if I lose the information
in the variable (say when I log out) I can recover it. Notice that this directory is ***not secure***!


Check on the Service Principal name: 


```
az ad sp list --show-mine --output table
```


The result is a bit hard to read but the second value should the the Service Principal name. I can use my browser
zoom to make everything small and fix the wrap format issue for a moment. 


At this point we can create the Azure kubernetes service (AKS) cluster.


```
az aks create \
   --name r5 \
   --resource-group r5-rg \
   --ssh-key-value ssh-key-r5.pub \
   --node-count 3 \
   --node-vm-size Standard_D2s_v3 \
   --service-principal $SP_ID \
   --client-secret $SP_PASSWD \
   --dns-service-ip 10.0.0.10 \
   --docker-bridge-address 172.17.0.1/16 \
   --network-plugin azure \
   --network-policy azure \
   --service-cidr 10.0.0.0/16 \
   --vnet-subnet-id $SUBNET_ID \
   --output table
```

This runs for a few minutes. Running as **`Owner`** with no policy restrictions in place on this subscription
allow this to go smoothly. In the process this creates a new resource group so that now the command

```
az group list --output table
```

returns both `r5-rg` and the new one: `MC_r5-rg_r5_westus`. The name of the new RG is an amalgam of the original resource group
name and the name of the AKS cluster and the region.


Now we turn to the kubernetes control system `kubectl`: Already installed on the Azure interactive shell. We need
operating credentials; so `next07.creds` reads: 


```
az aks get-credentials \
   --name r5 \
   --resource-group r5-rg \
   --output table
```

This operates behind the scenes; the only output is **`Merged "r5" as current context in /home/rob/.kube/config`**.
There is a config file in the indicated location; just credential data.


Now

```
kubectl get node
```

lists the three AKS VMs in the nodepool.


To list the AKS itself: 


```
az aks list --output table
```


To stop it: 


```
az aks stop --name r5 --resource-group r5-rg
```

And this takes a couple of minutes. 


When we continue it is the `helm` phase so start [here](https://zero-to-jupyterhub.readthedocs.io/en/latest/kubernetes/setup-helm.html)


## Install **`helm`**

What the hell is `helm`? Helm is a Kubernetes deployment tool for automating creation, 
packaging, configuration, and deployment of applications and services to Kubernetes clusters.


Like JupyterHub for example. 


Fortunately it is already installed on the Azure interactive shell. `helm version` to be convinced.


## My variables like `$VNET_ID` are wiped... do I care?


I went away and came back. Let's assume I do not need them until we learn otherwise.


## Install JupyterHub

- Created comment-full `config.yaml`
- Run the `helm upgrade --install` command: Requires the AKS to be turned ON if it is off



Output:

```
Release "jhub" does not exist. Installing it now.
NAME: jhub
LAST DEPLOYED: Fri May 27 21:53:36 2022
NAMESPACE: jhub
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
Thank you for installing JupyterHub!
Your release is named "jhub" and installed into the namespace "jhub".
You can check whether the hub and proxy are ready by running:
 kubectl --namespace=jhub get pod
and watching for both those pods to be in status 'Running'.
You can find the public (load-balancer) IP of JupyterHub by running:
  kubectl -n jhub get svc proxy-public -o jsonpath='{.status.loadBalancer.ingress[].ip}'
It might take a few minutes for it to appear!
To get full information about the JupyterHub proxy service run:
  kubectl --namespace=jhub get svc proxy-public
If you have questions, please:
  1. Read the guide at https://z2jh.jupyter.org
  2. Ask for help or chat to us on https://discourse.jupyter.org/
  3. If you find a bug please report it at https://github.com/jupyterhub/zero-to-jupyterhub-k8s/issues
```

Do the last three commands; there we have it.

```
az network vnet create \
   --resource-group r5-rg \
   --name r5-vnet \
   --address-prefixes 10.0.0.0/8 \
   --subnet-name r5-subnet \
   --subnet-prefix 10.240.0.0/16

----------------------------------------

VNET_ID=$(az network vnet show \
   --resource-group r5-rg \
   --name r5-vnet \
   --query id \
   --output tsv)

----------------------------------------

SUBNET_ID=$(az network vnet subnet show \
   --resource-group r5-rg \
   --vnet-name r5-vnet \
   --name r5-subnet  \
   --query id \
   --output tsv)

----------------------------------------
az ad sp create-for-rbac \
   --name r5-sp \
   --role Contributor \
   --scopes $VNET_ID

----------------------------------------

decea244-f240-4753-8c6d-04e62bbf29d4
..........password string deleted.........

----------------------------------------

az aks create \
   --name r5 \
   --resource-group r5-rg \
   --ssh-key-value ssh-key-r5.pub \
   --node-count 3 \
   --node-vm-size Standard_D2s_v3 \
   --service-principal $SP_ID \
   --client-secret $SP_PASSWD \
   --dns-service-ip 10.0.0.10 \
   --docker-bridge-address 172.17.0.1/16 \
   --network-plugin azure \
   --network-policy azure \
   --service-cidr 10.0.0.0/16 \
   --vnet-subnet-id $SUBNET_ID \
   --output table

----------------------------------------

az aks get-credentials \
   --name r5 \
   --resource-group r5-rg \
   --output table

----------------------------------------

HELM_RELEASE=jhub
K8S_NAMESPACE=jhub
HUB_CHART_VERSION=1.2.0
helm upgrade --cleanup-on-fail \
  --install $HELM_RELEASE jupyterhub/jupyterhub \
  --namespace $K8S_NAMESPACE \
  --create-namespace \
  --version=$HUB_CHART_VERSION \
  --values config.yaml

----------------------------------------

K8S_NAMESPACE=jhub
kubectl config set-context $(kubectl config current-context) --namespace $K8S_NAMESPACE

----------------------------------------

K8S_NAMESPACE=jhub
kubectl get pod --namespace $K8S_NAMESPACE

----------------------------------------

K8S_NAMESPACE=jhub
kubectl get service --namespace $K8S_NAMESPACE

```





