setwd('~/Documents/School/fall2020/bigData/finalProject')

library(data.table)
library(ggplot2)

# read in data
master_orders <- read.csv('data/bigfiles/master_orders.txt', header=TRUE, sep=',')
master_stores <- read.csv('data/bigfiles/master_stores.txt', header=TRUE, sep=',')

# add col with yr-month as the value
setDT(master_orders)[, yr_month := format(as.Date(createdAt), "%Y-%m") ]

# temporarily create PVD subset with just: Bajas Taqueria, Poke Works on Thayer
pvd_orders = subset(master_orders, master_orders$store == "5b4a618f326bd9777aa5dc58" 
                    | master_orders$store == "5b4a618f326bd9777aa5dc34")

# create counts for order data
activity <- pvd_orders[, .N, by=.(store, yr_month)]

# create plots
activity_plot = ggplot(activity, aes(yr_month, N, group=store, col=store)) + geom_point() + 
  geom_line() + ggtitle("Bajas and Pokeworks Activity")
plot(activity_plot)
