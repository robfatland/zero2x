After creating the **`r5-rg`** resource group; about 21 steps:

```
mkdir r5
cd r5
ssh-keygen -f ssh-key-r5
az network vnet create \
   --resource-group r5-rg \
   --name r5-vnet \
   --address-prefixes 10.0.0.0/8 \
   --subnet-name r5-subnet \
   --subnet-prefix 10.240.0.0/16
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
az ad sp create-for-rbac \
   --name r5-sp \
   --role Contributor \
   --scopes $VNET_ID

Using cut-and-paste:

SP_ID=<paste value>
SP_PASSWD=<paste value>

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
az aks get-credentials \
   --name r5 \
   --resource-group r5-rg \
   --output table

Edit config.yaml to be: 

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

helm repo add jupyterhub https://jupyterhub.github.io/helm-chart/
helm repo update
HELM_RELEASE=jhub
K8S_NAMESPACE=jhub
HUB_CHART_VERSION=1.2.0
helm upgrade --cleanup-on-fail \
  --install $HELM_RELEASE jupyterhub/jupyterhub \
  --namespace $K8S_NAMESPACE \
  --create-namespace \
  --version=$HUB_CHART_VERSION \
  --values config.yaml
kubectl config set-context $(kubectl config current-context) --namespace $K8S_NAMESPACE
kubectl get pod --namespace $K8S_NAMESPACE
kubectl get service --namespace $K8S_NAMESPACE
```
