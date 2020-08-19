
#INGREDIENTS WORDCLOUD

from wordcloud import WordCloud, STOPWORDS 
import matplotlib.pyplot as plt 
import pandas as pd 
  

df = pd.read_csv(path_file) 

d = {}
for a, x in df.values[2:]:
    d[a] = x

def plot_cloud(wordcloud):
    # Set figure size
    plt.figure(figsize=(40, 30))
    # Display image
    plt.imshow(wordcloud) 
    # No axis details
    plt.axis("off");

wordcloud = WordCloud(width = 3000, height = 2000, random_state=1, background_color='white', collocations=False, stopwords = STOPWORDS)
wordcloud.generate_from_frequencies(frequencies=d)
#wordcloud.to_file(path+"wordcloud2.png")





#NUMBER OF RECIPES PER REGION

import sys
'geopandas' in sys.modules
get_ipython().system('pip install geopandas')

import sys
import geopandas as gpd
import pandas as pd
italy = gpd.read_file(path1+'reg2011_g.shp')
new_regions = pd.read_csv(path2+"regionality_recipes.csv")
italy['NOME_REG'] = new_regions['region']
italy


new_regions = new_regions.rename(columns={"region": "NOME_REG"})
merge = italy.merge(new_regions, on='NOME_REG', how='right')
merge.head()


# set a variable that will call whatever column we want to visualise on the map
variable = 'recipes'
# set the range for the choropleth
vmin, vmax = 120, 220
# create figure and axes for Matplotlib
fig, ax = plt.subplots(1, figsize=(10, 6))

merge.plot(column=variable, cmap='Blues', linewidth=0.8, ax=ax, edgecolor='0.8')

ax.axis('off')


# add a title
ax.set_title('Recipes per Region', fontdict={'fontsize': '15', 'fontweight' : '2'})

# Create colorbar as a legend
sm = plt.cm.ScalarMappable(cmap='Blues', norm=plt.Normalize(vmin=min(merge['recipes']), vmax=max(merge['recipes'])))
# empty array for the data range
sm._A = []
# add the colorbar to the figure
cbar = fig.colorbar(sm)

#fig.savefig("recipes_per_region.png", dpi=300)






#Seaborn Histogram and Density Curve on the same plot

import pandas as pd
import seaborn as sns
sns.set_style("white")

# Import data
df = pd.read_csv(path+"regional_recipes_cat.csv")
df

x1 = df.loc[df.level=='Facile', 'ning']
x2 = df.loc[df.level=='Media', 'ning']
x3 = df.loc[df.level=='Difficile', 'ning']

# Plot
kwargs = dict(hist_kws={'alpha':.6}, kde_kws={'linewidth':2})


sns.distplot(x1, color="dodgerblue", label="Easy", **kwargs)
sns.distplot(x2, color="orange", label="Medium", **kwargs)
sns.distplot(x3, color="deeppink", label="Difficult", **kwargs)

plt.xlim(0,50)
plt.xlabel("Number of Ingredients in a Regional Recipe")
plt.ylabel("Density Function")
plt.legend()

#plt.savefig('pdf_ing.png')


# In[184]:


#BUBBLE CHART
import plotly.express as px

df = pd.read_csv(path+"recipes_cat.csv")

final = df.groupby(["category", "region"],as_index = False)["name"].count()
tmp2 = df.groupby(["category", "region"], as_index = False)["score"].mean()
tmp3 = df.groupby(["category", "region"], as_index = False)["reviews"].mean()
final["score"] = tmp2["score"]
final["reviews"] = tmp3["reviews"]


fig = px.scatter(final, x="reviews", y="score",
	         size="name", color="category",
                 hover_name="region", log_x=True, size_max=50)
#fig.show()
#fig.write_image(path+"bubble_plot.png")

