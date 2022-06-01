1. Decide upon a base resource string. I use `r5`. Substitute this in the first line of the script.
2. Start the interactive shell; at which point define a resource group called **`$BASE-rg`**
3. In the home directory create a `config.yaml` file for use by **`helm`**. 

Simplest is an empty file; or see the full notes for the 'dummy file with comments'; or one can be ambitious and use

```
singleuser:
  image:
    name: jupyter/datascience-notebook
    tag: latest
```

4. Run this script from the home directory 

```
BASE=r5
mkdir $BASE
cd $BASE
ssh-keygen -f ssh-key-$BASE
az network vnet create \
   --resource-group $BASE-rg \
   --name $BASE-vnet \
   --address-prefixes 10.0.0.0/8 \
   --subnet-name $BASE-subnet \
   --subnet-prefix 10.240.0.0/16
VNET_ID=$(az network vnet show \
   --resource-group $BASE-rg \
   --name $BASE-vnet \
   --query id \
   --output tsv)
SUBNET_ID=$(az network vnet subnet show \
   --resource-group $BASE-rg \
   --vnet-name $BASE-vnet \
   --name $BASE-subnet  \
   --query id \
   --output tsv)
az ad sp create-for-rbac \
   --name $BASE-sp \
   --role Contributor \
   --scopes $VNET_ID
```

5. From the last output above copy and past two variables:

```
SP_ID=<paste value>
SP_PASSWD=<paste value>
```

6. Run this script

```
echo $SP_ID > ~/.sp_details
echo $SP_PASSWD >> ~/.sp_details
az aks create \
   --name $BASE \
   --resource-group $BASE-rg \
   --ssh-key-value ssh-key-$BASE.pub \
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
   --name $BASE \
   --resource-group $BASE-rg \
   --output table
cp ../config.yaml .
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


7. The final command `kubectl get service` will initially give a public URL as "pending". Wait a bit and re-issue:


```
kubectl get service --namespace $K8S_NAMESPACE
```

8. Once it appears: Paste that URL into a browser.
