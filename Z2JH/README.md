Let's build [Jupyter Hub infrastructure](https://zero-to-jupyterhub.readthedocs.io/en/latest/)
on the Azure cloud. For this you need 


- an Azure subscription that is "clean" (not burdened by pre-existing restrictive policies)
- familiarity with Jupyter notebooks and Jupyter hubs (and a good reason to build one!)
- familiarity with issuing commands and editing text files in Linux (particularly creating and running scripts)
- a few hours to spare
    - First time this will be a bit slow to put together...
    - ...and if you make a mistake you may have to scrap everything and start over...
    - Once building a Jupyter Hub becomes second nature it goes pretty fast (half an hour)



## My FAQ


- Related links?
    - [Naomi's instructions](https://curious-poppyseed-2cf.notion.site/Script-draft-1-06700862a4da415b93ab079b24ce24df) are directional (get it done) whereas this here is 'notes'.
    - The original [ZeroToJupyterHub site](https://zero-to-jupyterhub.readthedocs.io/en/latest/) (can become outdated in some details)
    - An FAQ on the [Azure Kubernetes Service (AKS)](https://docs.microsoft.com/en-us/azure/aks/faq), the Azure service at the center of this procedure.
    - [This page](https://github.com/robfatland/zero2x/edit/master/Z2JH/README.md) and my [accelerator cheat sheet](https://github.com/robfatland/zero2x/blob/master/Z2JH/redux.md). 
        - After some practice I can build a data science Jupyter Hub in 10 minutes using the cheat sheet.
    - [Customizing the Jupyter environment](https://zero-to-jupyterhub.readthedocs.io/en/latest/jupyterhub/customization.html)
        - This is all about building, storing and invoking a custom Docker image that has desired whistles and bells
    


- What is a good scheme for naming the many Azure resources and services called into play here?
    - Choose a (short, simple) base string; and use that to name everything
    - I use **`r5`**: In the `bash` shell I define `BASE=r5` and then use $BASE
        - This is shown on the [accelerator cheat sheet](https://github.com/robfatland/zero2x/blob/master/Z2JH/redux.md)
    - Example: My starting resource group is `r5-rg`
 

- If I am interrupted mid-build: What becomes of my work?
    - Assuming I use the Azure portal's built-in interactive cloud shell... 
        - File system modifications persist (e.g. key pair files) 
        - Cloud resources (RG, vnet, subnet, AKS) persist
            - So to save $: **`stop`** the AKS; do not **`delete`** the AKS
    - environment variables evaporate
        - As we build: Save the create commands in a file for future reference
        - Alternative: Recover variable declarations from `history`


- No answers yet for: What is care and feeding of a JupyterHub about?
    - Part One: What is the complete "box of toys" including those generated automatically / invisibly
    - Part Two: What is likely to break or need attention in one / three / six / twelve / 24 months?
    - Part Three: When the team wants to install additional...?
        - Python modules (and how do ***environments*** factor in?)
        - Software, from MATLAB to Tableau


- What is a high-level breakdown of the JupyterHub build?
    - There is a core procedure to build a generic system; and then there is fine tuning details
        - Generic build
            - Create a private network 
            - Create an Azure Active Director **Service Principal** (acts like a friendly bot)
            - Create an Azure Kubernetes Service (AKS) instance: manages a 3 VM cluster
            - Use helm to install JupyterHub and provide a connection ip address
        - Fine tuning (not covered in these notes)
            - Customize the environment via a 'template' Docker image
            - Add user authentication access
            - Automate AKS to only be ON during weekday working hours
            - Enable users to turn the Jupyter Hub ON / OFF at other times
            - Associate a DNS entry with the JupyterHub service
            - Pay for the system monthly


Are there any gotchas?
    - Formatting commands is fraught with peril: An extra space here, a single hyphen when it should be double...
    - AKS Create fails with `RequestDisallowedByPolicy`: Some kind of restrictive policy must be voided
    - The generic install has absolutely no security around who can log in; so this is a key missing piece
    - Instructions given here are valid on 1-JUN-2022 but have a half-life as the Azure cloud evolves over time


- What will this cost?
    - The Standard_D2s_v3 instance costs $0.11 / hour and we allocate three of them
        - This is not 'elastic': They are all always on unless we stop AKS; then no cost
    - [Here is the AKS cost calculator](https://azure.microsoft.com/en-us/pricing/calculator/?service=kubernetes-service)
    - Bottom line: As configured here (I believe) $256/month running 24/74
        - Cost should scale with on-time so "work hours" should drop this to about $50 / month
    - How many Users does this support?


- What is a container-centric narrative of what happens here? 
    - We have some nodes (VMs) where the containers will live (inhabited by human researchers)
    - We have some sort of persistent storage *away* from the nodes where the home directory of the User is freeze dried when not in use
    - This implies that the container ***minus*** the home directory always begins an operational session in the same state
    - ...and this implies that anything *installed* in the OS (outside the home directory) will be gone next time


- Unanswered questions remain!
    - Should I do Littlest Jupyter Hub or this one?
    - How do I put the AKS on a Start/Stop timer?
    - Is a *cluster* a collection of *nodes*?
        - Sure
    - How many Users does this JupyterHub support? 
        - 30 pods per node, 3 nodes: 90 Users... 
            - But pods have a PVC of 10GB; and the OS disk size is 128GB so does the arithmetic work?
            - Perhaps we are counting on not having all 90 Users on the system at once.
    - Why use Helm with Kubernetes?
        - Customization. Helm is the K8 package manager; cf `config.yaml` below 
    - https how?
    - pre-install matplotlib etc how?
        - [Customization](https://zero-to-jupyterhub.readthedocs.io/en/latest/jupyterhub/customization.html)
        - Probably easy: Use a pre-built Docker container
        - Difficulty unknown: Add more yaml to `config.yaml`






## Notes from following the 'K8 on Azure' track of Zero To JupyterHub


- Navigate to the Azure-specific Z2JH [AKS instructions](https://zero-to-jupyterhub.readthedocs.io/en/latest/kubernetes/microsoft/step-zero-azure.html)
- Login to [Azure](https://portal.azure.com)
- Choose the correct subscription (the default filter can obscure this, unfortunately) and verify you are There
- Click the Azure interactive shell icon (upper right `>_` icon) to start the Azure interactive shell.
    - This is a `bash` shell with the `az` Azure command line interface pre-installed. It runs within your Azure portal window.
    - However it may start with 'You have no storage mounted' so we need a little sub-procedure to navigate this
        - Click on **`Show advanced settings`**
        - Ensure the subscription chosen is correct; as well as the region (in my case `West US`)
        - Resource group: Create new and provide a short unique identifier. I use `r5-rg`
        - Storage account: Likewise but it does not support hyphens so I use `r5sa`
        - File share: Likewise; I use `r5fs`
        - Click `Create storage` 
- Shell terminal opens


These **`az`** commands illustrate getting readable results by using `--output table`. Enter them if you
are interested in seeing what is going on. They are not part of the build procedure. For example the 
`az account set` command should be extraneous because you have already selected the correct subscription above.


```
az account list --refresh --output table
az account set --subscription 'rob5 teaching'
az account list --refresh --output table
```

This should show `True` under `Is Default` for the subscription we choose.


Above, when starting up the interactive shell, we created a resource group. Then we do not need to do that now. 
On the other hand if we did *not* do so before:  *Now* is the time. Choose a name aligned with this project. Note the
**region** designation is **`westus`** so use this consistently to keep all resource in the same data center.




```
az group create --name=r5-rg --location=westus --output table
```


Using the portal interface: The other approach to checking in on the resources and tagging them.


Tag the RG. This is done in the portal by selecting it and clicking the `edit` hyperlink after **Tags**.


Next make a directory with a familiar name, go there, create an ssh key pair.


```
mkdir r5
cd r5
ssh-keygen -f ssh-key-r5
ls -al
```


No passphrase is needed; and ignore the text printed as output as it will not come into play.
Notice that `r5` label in the `ssh-keygen` command: That will be the cluster name. There should
now be two ssh key files present. 


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


`echo $VAR_NAME` shows we got it right. The long hyphenated hexadecimal string is the subscription ID.


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


This gives four key-value pairs including an ID and a PASSWD. Using copy-paste I manually save two of these as temporary variables:


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


The DisplayName column should show the Service Principal you just created.


Now to create the Azure kubernetes service (AKS) cluster. Notice that this uses 
three variables we set above: **`SP_ID`**, **`SP_PASSWD`**, and **`SUBNET_ID`**.
The instance type and count for the cluster nodes is given (3) and some other
arcane things are included as well. 


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

This runs for a few minutes. Run as **`Owner`** with no policy restrictions in place on this subscription
and it should go smoothly. This procedure creates a new resource group. Verify by issuing:

```
az group list --output table
```

This returns both `r5-rg` and `MC_r5-rg_r5_westus`. The name of this new RG is an amalgam of the original 
resource group name, the name of the AKS cluster and the region.


Now we are done with the variables we have set to this point. We now turn to the kubernetes control system `kubectl`
and the `helm` configuration manager. Both are already installed on the Azure interactive shell. We need
operating credentials; so run a second `az aks` command:


```
az aks get-credentials \
   --name r5 \
   --resource-group r5-rg \
   --output table
```

This operates behind the scenes; the only output is **`Merged "r5" as current context in /home/rob/.kube/config`**.
This step creates a config file in the indicated location.  This is credential data.


Now run (for interest only):

```
kubectl get node
```

This lists the three AKS VMs in the nodepool for our interest/confirmation. The **`AKS`** service should also be 
visible within this RG on the portal. 


To list the AKS from the command line: 


```
az aks list --output table
```


While the AKS is running ot costs money. To continue the JupyterHub build: Keep going. 
To stop the AKS temporarily use:


```
az aks stop --name r5 --resource-group r5-rg
```

Stopping takes a couple of minutes. 


Now we proceed to the `helm` phase; [this link in the original documentation](https://zero-to-jupyterhub.readthedocs.io/en/latest/kubernetes/setup-helm.html).


## Using **`helm`**

What is `helm`? Helm is a Kubernetes deployment tool for automating creation, 
packaging, configuration, and deployment of applications and services to Kubernetes clusters.
Alternative definition: Helm is a package manager for kubernetes, specifically for
kubernetes clusters. 


In our case the 'service' we are deploying is JupyterHub. How to customization? As
noted above suppose the Users want `imbalanced-learn` pre-installed.


`helm` is already installed on the Azure interactive shell. Run `helm version` to be sure.


> ***Note: Shell variables like `VNET_ID` are no longer needed in this procedure.


## Install JupyterHub

- Created the following `config.yaml` (just a series of comments).
    - This is where that custom `imbalanced-learn` library will come up...


```
# This file can update the JupyterHub Helm chart's default configuration values.
#
# For reference see the configuration reference and default values, but make
# sure to refer to the Helm chart version of interest to you!
#
# Introduction to YAML:     https://www.youtube.com/watch?v=cdLNKUoMc6c
# Chart config reference:   https://zero-to-jupyterhub.readthedocs.io/en/stable/resources/reference.html
# Chart default values:     https://github.com/jupyterhub/zero-to-jupyterhub-k8s/blob/HEAD/jupyterhub/values.yaml
# Available chart versions: https://jupyterhub.github.io/helm-chart/
#
```

Don't do anything with this, it is just a placeholder for `config.yaml` content. 


```
singleuser:
  image:
    name: jupyter/datascience-notebook
    tag: latest
```


The following procedural steps create a repo entry in helm's repository table.


```
helm repo add jupyterhub https://jupyterhub.github.io/helm-chart/
helm repo update
helm repo list
```


Of interest (not procedural):


```
helm show values jupyterhub/jupyterhub > tmp_jhub.yaml
more tmp_jhub.yaml
```


This is a **lot** of information about the deployment. 


The following command `helm upgrade --install jupyterhub (etc)` references that jupyterhub repo.
It also references `config.yaml` which is where we want to stipulate 'install matplotlib and 
imbalanced-learn'. 


```
HELM_RELEASE=jhub
K8S_NAMESPACE=jhub
HUB_CHART_VERSION=1.2.0
helm upgrade --cleanup-on-fail \
  --install $HELM_RELEASE jupyterhub/jupyterhub \
  --namespace $K8S_NAMESPACE \
  --create-namespace \
  --version=$HUB_CHART_VERSION \
  --values config.yaml
```
  

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

Run the final three `kubectl` commands as follows:


```
kubectl config set-context $(kubectl config current-context) --namespace $K8S_NAMESPACE
kubectl get pod --namespace $K8S_NAMESPACE
kubectl get service --namespace $K8S_NAMESPACE
```

The context referred to is the cluster name `r5`. 


Note the public ip address from `get service`. Paste this in a browser address bar; 
and enter any username. This should yield a working Jupyter notebook server **pod**.


Using the `jhub` namespace we can check status: 


```
helm status jhub
```


Who is logged in? Use:


```
kubectl get pods
```


Memory capacity of various processes including pods? Pods use Persistent Volume Claims (PVCs) as volumes. 
The `get pvc` qualifiers show that pods have 10GB Persistent Volumes. 


```
kubectl get pvc
```


Suppose that we modified the container; and the `config.yaml`; how to rebuild? This: 


```
helm upgrade --cleanup-on-fail \
  $HELM_RELEASE jupyterhub/jupyterhub \
  --namespace $K8S_NAMESPACE \
  --version=$HUB_CHART_VERSION \
  --values config.yaml
```


## Appendix: Script files


Here are all of the files I generated, from `next01.vnet` ...to... `next11.kubectl_get_service`.
Please note: ***These files make it easier to create/fix the more complicated commands. 
The simpler commands are only given above in the procedural.***


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


## Appendix 2 Debugging issue


We saw an issue come up; I'm copying the dialog towards eventually capturing this in the procedural notes.


Learner writes:


```
...trying to finish up the DNS, HTTPs, and auth steps. I successfully set the domain name on the jupyter config. 
When I edited the config.yaml again for the https portion helm upgraded successfully, but when accessing the 
website I see an https error instead of the Jupyter login. I’m not sure if this is due to an issue in my config.yaml 
or something I need to do to enable letsencrypt?

 

Webpage error:

An error occurred during a connection to aa.aa.aa.aa. Peer reports it experienced an internal error.

Error code: SSL_ERROR_INTERNAL_ERROR_ALERT

 

My config.yaml:

 

proxy:

  service:

    annotations:

      service.beta.kubernetes.io/azure-dns-label-name: xxxxxxxx-k8s-demo

  https:

    enabled: true

    hosts:

      - xxxxxxxx-k8s-demo.centralus.cloudapp.azure.com

    letsencrypt:

      contactEmail: xxxxxxxx@xx.xxx

singleuser:

  image:

    # You should replace the "latest" tag with a fixed version from:

    # https://hub.docker.com/r/jupyter/datascience-notebook/tags/

    # Inspect the Dockerfile at:

    # https://github.com/jupyter/docker-stacks/tree/HEAD/datascience-notebook/Dockerfile

    name: jupyter/datascience-notebook

    tag: latest
```


Our team replies:


```
The first thing you can do is run `kubectl top pod --namespace=jhub` to list all of the active pods (running docker containers) 
in your cluster. This reveals:

NAME                              CPU(cores)   MEMORY(bytes)  
autohttps-aaaaaaaaa-gdkk9         1m           69Mi            
continuous-image-puller-c6sxk     0m           0Mi            
continuous-image-puller-hdftk     0m           0Mi            
continuous-image-puller-qb8vm     0m           0Mi            
hub-aaaaaaaaaa-p7kh9              3m           107Mi          
jupyter-randomuser                1m           190Mi          
proxy-aaaaaaaaaa-99w8z            1m           15Mi            
user-scheduler-aaaaaaaaaa-fz6bp   2m           17Mi            
user-scheduler-aaaaaaaaaa-jzz4d   2m           20Mi  

I'm interested in that 'autohttps' pod, because it sounds like it has something to do with working out HTTPS. 
To view logs from it, run this command:

`kubectl --namespace=jhub logs pod/autohttps-aaaaaaaaaa-gdkk9`

and this returns:

Defaulted container "traefik" out of: traefik, secret-sync, load-acme (init)
time="2022-05-31T20:11:57Z" level=info msg="Configuration loaded from file: /etc/traefik/traefik.yaml"
time="2022-05-31T20:11:57Z" level=warning msg="No domain found in rule PathPrefix(`/`), the TLS options 
applied for this router will depend on the hostSNI of each request" entryPointName=https routerName=default@file
time="2022-05-31T20:11:59Z" level=warning msg="No domain found in rule PathPrefix(`/`), the TLS options 
applied for this router will depend on the hostSNI of each request" routerName=default@file entryPointName=https
time="2022-05-31T20:12:14Z" level=error msg="Unable to obtain ACME certificate for domains \"xxxxxxxx-k8s-demo.centralus.cloudapp.azure.com\" : 
unable to generate a certificate for the domains [xxxxxxxx-k8s-demo.centralus.cloudapp.azure.com]: error: one or more domains had a 
problem:\n[xxxxxxxx-k8s-demo.centralus.cloudapp.azure.com] acme: error: 400 :: urn:ietf:params:acme:error:dns :: 
DNS problem: SERVFAIL looking up CAA for azure.com - the domain's nameservers may be malfunctioning\n" providerName=default.acme
time="2022-05-31T20:21:57Z" level=warning msg="A new release has been found: 2.7.0. Please consider updating."


Now we have meaningful server logs to debug!


Judging by these logs, it sounds like the fatal issue was 'DNS problem: SERVFAIL looking up CAA for azure.com - the domain's nameservers may 
be malfunctioning' . My guess is that not enough time had passed for the hub's DNS entries to settle down, and so certificate acquisition 
failed. The first thing I would try is just re-running the 'helm upgrade', now that some time has passed.
```


Response from Learner:


```
I ran kubectl delete pod autohttps-aaaaaaaaa-gdkk9 then re-ran the helm upgrade to re-create the autohttps pod.

 

The only other issue I ran into in setting up auth with github is that your sample config for openauth includes a tab instead of two spaces on the “Authenticator” (bolded below) line, which cause helm upgrade to throw a yaml error:

 

hub:

  config:

    GitHubOAuthenticator:

      client_id: <your-client-id>

      client_secret: <your-client-secret>

      oauth_callback_url: https://<your domain>/hub/oauth_callback

    JupyterHub:

      authenticator_class: github

                Authenticator:

      admin_users:

        - <your github username>
```


