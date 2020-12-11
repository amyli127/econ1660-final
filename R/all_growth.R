library(data.table)
library(ggplot2)

# read in data
# master_orders <- fread('data/bigfiles/master_orders.txt')
# pvd_stores <- fread('data/smallfiles/pvd_stores.txt')
# setnames(pvd_stores, "_id", "id")
# datetime <- fread('data/bigfiles/datetime.txt')

# merge data
orders <- master_orders[datetime, on = .(createdAt = createdAt), nomatch = 0]
orders[, year_month := format(as.Date(ISOdate(month = orders$month, year = orders$year, day = 1)), "%m/%y")]

# filter to jan 1 2018
orders <- orders[orders$year >= 2018,]
orders <- orders[!(orders$year == 2020 & orders$month == 11),]

orders$year_month <- factor(orders$year_month, 
                                levels = c("01/18", "02/18", "03/18", "04/18", "05/18", "06/18", "07/18", "08/18", "09/18", "10/18", "11/18", "12/18",
                                           "01/19", "02/19", "03/19", "04/19", "05/19", "06/19", "07/19", "08/19", "09/19", "10/19", "11/19", "12/19",
                                           "01/20", "02/20", "03/20", "04/20", "05/20", "06/20", "07/20", "08/20", "09/20", "10/20"))

orders_grouped <- orders[order(year_month), .N, by = .(year, month)]

orders_grouped[, yoy := round(100 * (orders_grouped$N - shift(orders_grouped$N, 12)) / shift(orders_grouped$N, 12), 2)]
orders_grouped <- orders_grouped[orders_grouped$year > 2018,]

yoy_growth <- ggplot(orders_grouped, aes(fill = as.factor(year), y = yoy, x = as.factor(month))) +
      geom_bar(position="dodge", stat="identity") +
      scale_y_continuous(limits = c(-100,350)) +
      ggtitle("Year-Over-Year Growth In Snackpass Monthly Order Activity In All Markets") +
      ylab("% Change in # Orders") +
      xlab("Month") +
      labs(fill = "Years", caption = "Data collected Jan 2018 - Oct 2020") +
      scale_fill_discrete(labels = c("2018-2019", "2019-2020")) +
      scale_x_discrete(breaks = c("1","2","3","4","5","6","7", "8", "9", "10", "11", "12"), labels=c("Jan","Feb","Mar","Apr","May","Jun","Jul", "Aug", "Sep", "Oct", "Nov", "Dec"))

plot(yoy_growth)
