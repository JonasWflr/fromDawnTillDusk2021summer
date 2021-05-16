# from Dawn till Dusk
creating a streamlit webpage showing race data for the 'from Dawn till Dusk' event.

It retrievs data from a google spreadsheet and displays it in different charts.
A logic based on the date, determins what to show. I.e. only show the plots at the day or later, not before.

In one version I was reading many content blocks from a google spreadsheet, this made the website slow (see FromDawnTilDusk_spreadsheet_content.py), I changed it back to hard coded. Deployment is fairly easy and quick, so no need for unnecessary complexity.

## Hint
make sure that the spreadsheet REALLY is readable

## local development
open anaconda prompt, go to folder with local repo.
create or activate a new conda environment. 
check if you already have one that fits:
```
conda info -e
```
then activate it 
```
conda activate [blabla]
```

now you can work on the project. The easiest way, is to run it locally with streamlit and when ready, one runs it locally in a docker container, if that works as well, one can deploy it to azure.

### run it with streamlit
Locally you start the app with this command:
```
streamlit run FromDawnTilDusk.py
```

### run it with docker (locally)
```
docker build -t DawnTillDusk:latest .

docker container run -p 8501:8501 --name DawnTillDusk DawnTillDusk:latest
```


## deployment with Azure CLI

Install Azure CLI, then do the following:
```
az login
az account set --subscription "<SUBSCRIPTION>"
az acr build --registry <ACR-NAME> --image <IMAGE-NAME>:v0.01 .
```
Second command is only necessary when there are several subsciptions, choose 'name' from output.
Third command requires an ACR, this is set up easiest in portal.azure.com

After that, go to portal.azure.com, create a wep app, choose docker based, ACR and choose your image.
Et voilà, your webapp is running.

This one is running on:
```
https://dawntilldusk.azurewebsites.net/
```

# GIT (just because I tend to forget it every time)

1) init locally
2) add stuff
3) create repo online
4) link local to remote repo and push

### in more details:
go to folder with all the files
```
git init
git add .
git commit -m 'message'
```
Go to **github.com** and create my repo **fromDawnTillDusk2021summer**.

Then push it to my remote repo:
```
git remote add origin https://github.com/JonasWflr/fromDawnTillDusk2021summer.git
git push -u origin master
```

# ressources
how to get data from public google spreadsheets:
https://stackoverflow.com/questions/33713084/download-link-for-google-spreadsheets-csv-export-with-multiple-sheets
