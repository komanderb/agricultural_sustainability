# Sustainability Index

This repo contains the code for creating the sustainability index described in the 
methodology file. 
The idea is to create an sustainability/fragility index based on the change of agricultural production under different 
Relative Concentration Pathways (RCP's).
Moreover, instead of aggregating the data on the country level, this index is gridded, in cells sized roughly 10x10km.
Moreover varieties of the index take both gridded gdp and population growth into account. 

### Visualization
Go to this [little dashboard](https://komanderb.shinyapps.io/fragility_dashboard/) for a small visualization. Note that this shows just some of the data in a very basic way.

### Sources
Agricultural Data: [Gaez v4](https://gaez.fao.org/)

Gridded GDP: [Global gridded GDP data set consistent with the shared socioeconomic pathways](https://zenodo.org/record/5880037#.Y5BneXbMKUk)

[Paper](https://www.nature.com/articles/s41597-022-01300-x#Sec2)

Gridded Population [GPW v.4](https://sedac.ciesin.columbia.edu/data/collection/gpw-v4/sets/browse)


The final output of this repo is a data frame will all the data in interest. The `data` folder contains some basic files but otherwise relate. Otherwise refer to the google drive. 
Some of the measures (prices, caloric yield) are subject to change. 