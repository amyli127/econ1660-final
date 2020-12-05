library(data.table)
library(ggplot2)

# read in data
master_orders <- read.csv('data/bigfiles/master_orders.txt', header=TRUE, sep=',')
pvd_stores <- read.csv('data/smallfiles/pvd_stores.txt', header=TRUE, sep=',')
datetime <- read.csv('data/bigfiles/datetime.txt', header=TRUE, sep=',')
master_orders_w_date <- merge(master_orders, datetime, by = "X_id")

mex_store_names <- c("Bajas Taqueria", "Bajas Tex Mex", "Caliente Mexican Grill")
mex_store_ids <- pvd_stores[pvd_stores$name %in% mex_store_names, "X_id"]

master_orders_w_date$date_hour = paste(master_orders_w_date$date, master_orders_w_date$hour, sep="-")

mex_orders <- master_orders_w_date[master_orders_w_date$store %in% mex_store_ids, ]
mex_orders_merged <- merge(x = mex_orders, y = pvd_stores, by.x = "store", by.y = "X_id")

mex_orders_dt <- setDT(mex_orders_merged)
mex_activity <- mex_orders_dt[, .N, by=.(name, date_hour)]

mex_activity_plot <- ggplot(mex_activity, aes(date_hour, N, group = name, color = name)) + 
      geom_line() +
      ggtitle("Mexican Restaurants on Thayer") +
      ylab("Order Count") +
      xlab("Time") +
      scale_color_discrete(name = "Stores") +
      theme(axis.text.x=element_blank(),
           axis.ticks.x=element_blank(),
           panel.grid = element_blank()) +
      ylim(0, 70)

plot(mex_activity_plot)

