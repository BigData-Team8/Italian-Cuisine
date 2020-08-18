library(forcats)
library(ggplot2)
library(ggridges)
theme_set(theme_ridges())

df = read.csv(path+"regional_kcal.csv")

ggplot(
  df, 
  aes(x = `kcal`, y = fct_reorder(`region`, `kcal`, mean))
) +
  geom_density_ridges_gradient(
    aes(fill = ..x..), scale = 3, size = 0.3, quantile_lines = TRUE
  ) +
  scale_fill_gradientn(
    colours = c("#0D0887FF", "#CC4678FF", "#F0F921FF"),
    name = "kcal"
  )+
  labs(title = 'Calories in Italian Regional Recipes') 

