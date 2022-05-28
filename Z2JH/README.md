[Home page of this repository](https://github.com/robfatland/zero2x/blob/master/README.md)


Let's have some fun building [Jupyter Hub infrastructure](https://zero-to-jupyterhub.readthedocs.io/en/latest/)
on Azure.



## The FAQ


- Any supporting links?
    - [The Naomi Formulation](https://curious-poppyseed-2cf.notion.site/Zero-To-Jupyterhub-Script-83866ee697964443a579d5b3f2500e4b)
    - Original [ZeroToJupyterHub site](https://zero-to-jupyterhub.readthedocs.io/en/latest/) (can become outdated in some details)
    - An FAQ on the [Azure Kubernetes Service (AKS)](https://docs.microsoft.com/en-us/azure/aks/faq) for orchestrating containers
    - [This page (you may already be here)](https://github.com/robfatland/zero2x/edit/master/Z2JH/README.md)


- As we proceed with creating many Azure resources: Good naming scheme?
    - I chose a short base string `r5`, then...
    - ...for each resource: Add a hyphen and short qualifier
    - Example: A resource group and a service principal are respectively `r5-rg` and `r5-sp`
        - (A service principal is an automaton or agent that acts on our behalf on Azure)
    - Exception: At the end of this build process the directions suggest more generic names e.g. `jhub`


- If I am interrupted mid-build: What becomes of my work?
    - Assuming the interactive cloud shell 
    - File system modifications persist (e.g. key pair files) 
    - Cloud resources (RG, vnet, subnet, AKS) persist so **`stop`** the AKS
    - environment variables evaporate
        - If necessary (and it may not be): We can recover those e.g. using `history`


- What is care and feeding of a JupyterHub about?
    - Part One: What is the complete "box of toys" including those generated automatically / invisibly
    - Part Two: What is likely to break or need attention in one / three / six / twelve / 24 months?
    - Part Three: When the team wants to install additional...?
        - Python modules (and how do ***environments*** factor in?)
        - Software, from MATLAB to Tableau


- What is the Z2JH the high-level breakdown?
    - Set up Kubernetes (K8) plus Helm
        - What is all this `RequestDisallowedByPolicy` business?
            - Answer: It is an exception that blocks the build if we the Azure User are encumbered by some policy
    - Install Jupyter Hub
    - Administrate
    - Pay for it


- What will this cost?
    - The Standard_D2s_v3 instance costs $0.11 / hour and we allocate three of them
        - This is not 'elastic': They are all always on unless we stop AKS; then no cost
    - [Here is the AKS cost calculator](https://azure.microsoft.com/en-us/pricing/calculator/?service=kubernetes-service)
    - Bottom line: As configured here (I believe) $256/month running 24/7
    - How many Users does this support?


- Should I do Littlest Jupyter Hub or this one?


- How do I put the AKS on a Start/Stop timer?


- Is a *cluster* a collection of *nodes*?


- If Kubernetes is container orchestration, why the extra step to Helm to manage Kubernetes? 


- What is a container-centric narrative of what happens here? 
    - We have some nodes (VMs) where the containers will live (inhabited by human researchers)
    - We have some sort of persistent storage *away* from the nodes where the home directory of the User is freeze dried when not in use
    - This implies that the container ***minus*** the home directory always begins an operational session in the same state
    - ...and this implies that anything *installed* in the OS (outside the home directory) will be gone next time



## Notes from following K8 on Azure


- Navigate to the Azure-specific Z2JH [AKS instructions](https://zero-to-jupyterhub.readthedocs.io/en/latest/kubernetes/microsoft/step-zero-azure.html)
- Login to [Azure](https://portal.azure.com)
- Choose the correct subscription (the default filter can obscure this, unfortunately) and verify you are There
- Click the Azure interactive shell icon (upper right) to use the `az` Azure command line.
    - In so doing: Use **Advanced Settings** to create a Resource Group under this subscription; select `bash` 
    - I name the RG `r5-rg`, the Storage Account `r5sa`, the File Share `r5-fs`
        - The `-` character is not permitted in storage account names, forsooth. 
- Shell terminal opens


These **`az`** commands illustrate getting readable results by using `--output table`


```
az account list --refresh --output table
az account set --subscription 'rob5 teaching'
az account list --refresh --output table
```

This should show `True` under `Is Default` for the subscription we choose.


Above, when starting up the interactive shell, we created a resource group. Then we do not need to do that now. 
On the other hand if we did *not* then *now* is the time. Choose a name aligned with this project.




```
az group create --name=r5-rg --location=westus --output table
```


Using the portal interface: The other approach to checking in on the resources and tagging them.


Tag the RG.


Next make a directory with a familiar name, go there, create an ssh key pair.


```
mkdir r5
cd r5
ssh-keygen -f ssh-key-r5
ls -al
```


Ignore the text printed in the last step; it will not come into play.
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


I call this `next01.vnet` and run it with `source next01.vnet`. It takes a minute and dumps some JSON if it works.
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


`echo $VAR_NAME` shows we got it right.


Next: Create a 'Service Principal' (an agent who operates on Azure) using Azure Active Directory.
Asking the internet to define a Service Principal is a descent into madness because the topic
is so overloaded with vagueon. vagueon is defined as incomprehensibly vague jargon. For example: 


> Service Principals are identities used by created applications, services, and automation tools to access specific resources. 


For my purposes, for now, a service principal is some kind of robot with permission to do stuff in my Azure subscription.


```
az ad sp create-for-rbac \
   --name r5-sp \
   --role Contributor \
   --scopes $VNET_ID
```


This gives four key-value pairs including an ID and a PASSWD; so by copy-paste I manually set two of these:


```
SP_ID=<paste value>
SP_PASSWD=<paste value>
```


I echoed these values into a file called `next05.sp-info` so that if I lose the information
in the variable (say when I log out) I can recover it. 


> *Notice that this directory is **not secure**!*


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

Run the final three commands; get the public ip address; should yield a working Jupyter notebook server.

Here are all of the files I generated, from `next01.vnet` ...to... `next11.kubectl_get_service`

```
01:
az network vnet create \
   --resource-group r5-rg \
   --name r5-vnet \
   --address-prefixes 10.0.0.0/8 \
   --subnet-name r5-subnet \
   --subnet-prefix 10.240.0.0/16

----------------------------------------

02:
VNET_ID=$(az network vnet show \
   --resource-group r5-rg \
   --name r5-vnet \
   --query id \
   --output tsv)

----------------------------------------

03:
SUBNET_ID=$(az network vnet subnet show \
   --resource-group r5-rg \
   --vnet-name r5-vnet \
   --name r5-subnet  \
   --query id \
   --output tsv)

----------------------------------------

04:
az ad sp create-for-rbac \
   --name r5-sp \
   --role Contributor \
   --scopes $VNET_ID

----------------------------------------

05 (information, not a script):
decea244-f240-4753-8c6d-04e62bbf29d4
..........password string redacted.........

----------------------------------------

06:
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

07:
az aks get-credentials \
   --name r5 \
   --resource-group r5-rg \
   --output table

----------------------------------------

08:
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

09:
K8S_NAMESPACE=jhub
kubectl config set-context $(kubectl config current-context) --namespace $K8S_NAMESPACE

----------------------------------------

10:
K8S_NAMESPACE=jhub
kubectl get pod --namespace $K8S_NAMESPACE

----------------------------------------

11:
K8S_NAMESPACE=jhub
kubectl get service --namespace $K8S_NAMESPACE

```





