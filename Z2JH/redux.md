1. Decide upon a **`BASE`** resource name; a short relevant string. I use `r5`. 
2. Start the interactive shell--being careful to select the intended subscription--and in so doing create an RG called **`$BASE-rg`**
3. In **`~`** create `config.yaml` that looks as follows: 

```
singleuser:
  image:
    name: jupyter/datascience-notebook
    tag: latest
```

4. Create a script as follows, taking care to substitute *your* base string for `r5` in line 1... oh, and then run it.


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

5. From the last four lines of output text: Copy and past to set two variables:


```
SP_ID=<paste value from above>
SP_PASSWD=<paste value from above>
```


6. Create and run the script below. You do this *in* the directory created above, $BASE. You should not have to change directories to do this.


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
sleep 20
kubectl get service --namespace $K8S_NAMESPACE
```


7. If the final output gives a public URL as "pending": You will have to re-run the
final command after a brief pause:


```
kubectl get service --namespace $K8S_NAMESPACE
```

8. Once the ip address appears in the output: Paste that URL into a browser. Any login combination will work: There is no authentication yet.



> Note: The auto-generated RG has a public ip address as one of its resources. We can click on this and
> in turn find that it does indeed have an ip address; but it is not useful. It is not the same
> as the ip address referred to above. Use the one above to connect to the Jupyter Hub. 

## Adding in additional features


### DNS entry through authentication


Following the narrative on [this documentation page](https://docs.microsoft.com/en-us/azure/aks/static-ip#apply-a-dns-label-to-the-service).


Find the public ip address in the automatically-generated RG **`MC_r5-rg_r5_westus`**.
Replace the ip address ***name*** in the following command with its name (not an actual ip address).
Make sure the resource-group name is correct.


```
az network public-ip create \
    --resource-group MC_r5-rg_r5_westus \
    --name some-hex-8-4-4-12-name \
    --sku Standard \
    --allocation-method static
```


The output is some descriptive JSON. 




