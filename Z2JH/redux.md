1. Decide upon a **`BASE`** resource name; a short relevant string. I use `r5`. 
2. Start the interactive shell 
    - ***being careful to select the intended subscription*** and in this process...
    - Use **See advanced settings** to create a Resource Group **`$BASE-rg`** in addition to a couple other items
    - It is best not to refresh your browser when the interactive shell is busy: It tends to lose the window and go into a "???" state


> Tip: There are several icons on the toolbar above the `bash` window for the interactive shell. 
> If for some reason you need to start over: Click the icon that looks like a power button. This will scrap and re-start
> the interactive shell. 



3. In **`~`** create `config.yaml` to look as follows: 

```
singleuser:
  image:
    name: jupyter/datascience-notebook
    tag: latest
```

4. Create a script as below; and substitute *your* base string for `r5` in line 1. I call my script `go1.script` 
and I run it with `source go1.script`. 


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


5. From the the output text: Identify the ID and Password; and copy their values into these two variables:


```
SP_ID=<paste value from above>
SP_PASSWD=<paste value from above>
```


6. Create and run the script below. You do this *in* the directory created above, `$BASE`. 
You should not have to change directories to do this. It should take 10 to 15 minutes or so.


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



> **Heads Up***: The script above auto-generates a new Resource Group. It has a name like **`MC_r5-rg_r5_westus`**.
> This is the **node** resource group.
> It contains two public ip addresses in its resource list. The one that looks like **`kubernetes-a47382...etcetera...`**
> is the one associated with the Jupyter Hub service. Open this resource and the ip address shown should match that provided in 
> step 8 above. Note that this public ip address has a **name** which is just that **`kubernetes-a47382...etcetera...`**
> string. Both this name and the name of the auto-generated resource group are used in the next step.


## Adding in additional features


### DNS entry through authentication


Following the narrative on [this documentation page](https://docs.microsoft.com/en-us/azure/aks/static-ip#apply-a-dns-label-to-the-service).


Find the **`kubernetes-etc`** public ip address within the automatically-generated RG that has a name like **`MC_r5-rg_r5_westus`**.
Place this RG name and the ip address ***name*** into the following command. 


```
az network public-ip create \
    --resource-group MC_r5-rg_r5_westus \
    --name kubernetes-aaaaaaaabbbbbbbbccccccccdddddddd \
    --sku Standard \
    --allocation-method static
```


The output is some descriptive JSON. 




