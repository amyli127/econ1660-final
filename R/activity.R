library(data.table)
library(ggplot2)

# read in data
master_orders <- read.csv('data/bigfiles/master_orders.txt', header=TRUE, sep=',')
pvd_stores <- read.csv('data/smallfiles/pvd_stores.txt', header=TRUE, sep=',')

# create subset with just PVD orders
pvd_orders = subset(master_orders, master_orders$store %in% pvd_stores$X_id)

# add col with yr-month as value
setDT(pvd_orders)[, yr_month := format(as.Date(createdAt), "%Y-%m") ]

# create counts for order data
activity <- pvd_orders[, .N, by=.(store, yr_month)]

# bind with column that maps store id to store name
activity_stores <- merge(x=activity, y=pvd_stores, by.x="store", by.y="X_id", all.x=TRUE)

# create plots
activity_plot = ggplot(activity_stores, aes(yr_month, N, group=name, col=name)) +
  geom_point() + geom_line() + ggtitle("Providence Restaurant Activity")
plot(activity_plot)
