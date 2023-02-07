
import pandas as pd
import requests

# Utils
import json
from pandas import json_normalize
import enum

from google.cloud import bigquery

# Options
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)

headers = {'Content-Type': 'application/json'}


# In[2]:


#import os
#from google.cloud import secretmanager
#secrets = secretmanager.SecretManagerServiceClient()

#resource_name = f"{os.environ['KNADA_TEAM_SECRET']}/versions/latest"
#secret = secrets.access_secret_version(name=resource_name)
#data = secret.payload.data.decode('UTF-8')


# ### Config

# In[3]:


class TeamType(enum.Enum):
    PRODUCT = "Produktteam"
    IT = "IT-team"
    ADMINISTRATION = "Forvaltningsteam"
    PROJECT = "Prosjektteam"
    OTHER = "Annet"
    UNKNOWN = "Ukjent"


# In[4]:


class AreaType(enum.Enum):
    IT = "IT-område"
    PRODUCT_AREA = "Produktområde"
    PROJECT = "Prosjekt"
    OTHER = "Annet"


# ### Get Data

# In[5]:


df_productarea = pd.DataFrame()
url = 'https://teamkatalog-api.nais.adeo.no/productarea'
r = requests.get(url, headers=headers)
content = r.json()['content']
normalized = json_normalize(content)
df_productarea = df_productarea.append(normalized, sort=True)
df_productarea['member-list'] = df_productarea['members'].apply(lambda x: json_normalize(x).to_records())


# In[6]:


df_productarea.head(1)


# In[7]:


df_productarea = df_productarea.drop(columns=['changeStamp.lastModifiedBy'])


# In[8]:


df_productarea.dtypes


# In[9]:


def convert_area_type(area_type):
    if area_type:
        return AreaType[area_type].value
    else:
        return AreaType.OTHER.value


# In[10]:


df_productarea["areaType"] = df_productarea["areaType"].apply(convert_area_type)


# In[11]:


df_productarea.columns = df_productarea.columns.str.replace('.', '_')


# In[12]:


df_teams = pd.DataFrame()
url = 'https://teamkatalog-api.nais.adeo.no/team'
#url = 'https://teamkatalog-api.prod-fss-pub.nais.io/team'
r = requests.get(url, headers=headers)
content = r.json()['content']
normalized = json_normalize(content)
df_teams = df_teams.append(normalized, sort=True)
df_teams['member-list'] = df_teams['members'].apply(lambda x: json_normalize(x).to_records())


# In[13]:


df_teams.head(1)


# In[14]:


df_teams.dtypes


# In[15]:


df_teams = df_teams.drop(columns=['changeStamp.lastModifiedBy'])


# In[16]:


def convert_team_type(team_type):
    return TeamType[team_type].value


# In[17]:


df_teams.columns = df_teams.columns.str.replace('.', '_')


# ### Publish data to BigQuery

# In[18]:


#Navn på prosjekt og dataset som definert i BigQuery
project_id = 'org-prod-1016'
dataset = 'teamkatalogen'

client = bigquery.Client(project=project_id)


# In[19]:


df_teams_pub= df_teams.copy()


# In[20]:


df_teams_pub = df_teams_pub.astype({ 'clusterIds': 'string','links_slackChannels': 'string', 'members': 'string', 'member-list': 'string'})


# In[21]:


#Istedenfor å spesifisere typen på variablene så plukker vi ut én kolonne til å teste med.
#df_teams_pub = df_teams_pub[['name']]


# In[22]:


#df_teams_pub[['name']]


# In[23]:


#df_teams_pub = df_teams_pub.head(1)


# In[24]:


table = 'teams'
destination_table = f"{project_id}.{dataset}.{table}"

job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE",)
job = client.load_table_from_dataframe(df_teams_pub, destination_table, job_config=job_config)
job.result()


# In[ ]:
