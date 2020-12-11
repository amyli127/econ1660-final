library(data.table)
library(ggplot2)

# read in data
# master_orders <- fread('data/bigfiles/master_orders.txt')
# pvd_stores <- fread('data/smallfiles/pvd_stores.txt')
# setnames(pvd_stores, "_id", "id")
# datetime <- fread('data/bigfiles/datetime.txt')

# merge data
pvd_orders <- master_orders[pvd_stores, on = .(store = id), nomatch = 0]
pvd_orders <- pvd_orders[datetime, on = .(createdAt = createdAt), nomatch = 0]
pvd_orders[, year_month := format(as.Date(ISOdate(month = pvd_orders$month, year = pvd_orders$year, day = 1)), "%m/%y")]

# filter to jan 1 2018
pvd_orders <- pvd_orders[pvd_orders$year >= 2018,]
pvd_orders <- pvd_orders[!(pvd_orders$year == 2020 & pvd_orders$month == 11),]

restaurant_counts <- pvd_orders[, .N, by = .(name)]
top_10_restaurants <- restaurant_counts[order(-N), name][1:10]

top_10_orders <- pvd_orders[pvd_orders$name %in% top_10_restaurants, ]
top_10_orders_grouped <- top_10_orders[, .N, by = .(name, year_month)]

top_10_orders_grouped$year_month <- factor(top_10_orders_grouped$year_month, 
                                           levels = c("01/18", "02/18", "03/18", "04/18", "05/18", "06/18", "07/18", "08/18", "09/18", "10/18", "11/18", "12/18",
                                                      "01/19", "02/19", "03/19", "04/19", "05/19", "06/19", "07/19", "08/19", "09/19", "10/19", "11/19", "12/19",
                                                      "01/20", "02/20", "03/20", "04/20", "05/20", "06/20", "07/20", "08/20", "09/20", "10/20"))

top_10_plot <- ggplot(top_10_orders_grouped, aes(year_month, N, group = name, color = name)) +
      geom_line() +
      ggtitle("Order Activity at 10 Most Popular Snackpass Restaurants in Providence") +
      ylab("# Orders") +
      xlab("Month") +
      scale_color_discrete(name = "Restaurants") +
      annotate("rect", xmin = 27, xmax = 30, ymin = -Inf, ymax = Inf, 
               alpha = .3) +
      labs(caption = "Data collected Jan 2018 - Oct 2020\nShaded region represents COVID-19 lockdowns") +
      theme(axis.text.x = element_text(angle = 90, vjust = 0.5))

plot(top_10_plot)