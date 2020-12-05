
library(data.table)
library(ggplot2)

#master_orders <- fread('data/bigfiles/master_orders.txt')
#master_orders_sorted <- master_orders[order(createdAt)]

# CAN DO THIS FASTER
# master_orders_sorted_first_two <- master_orders_sorted[, .SD[1:2], fromUser]
# setkey(master_orders_sorted_first_two,createdAt)

#datetime <- fread('data/bigfiles/datetime.txt')
#setkey(datetime,createdAt)

# master_orders_sorted_first_two <- master_orders_sorted_first_two[datetime, nomatch=0]

# diff = 0 -> only 1 order ever
# master_orders_sorted_first_two[ , diff := secs_since_epch - shift(secs_since_epch), by = fromUser] 
# master_orders_sorted_first_two <- master_orders_sorted_first_two[diff > 0]

# master_orders_sorted_diffs <- master_orders_sorted_first_two[, c("fromUser", "diff")]
# master_orders_counts <- master_orders[, .N, fromUser]

#setkey(master_orders_sorted_diffs,fromUser)
#setkey(master_orders_counts,fromUser)

# master_orders_diff_count <- master_orders_sorted_diffs[master_orders_counts, nomatch=0]

# fix up plot
#correlation between time from 1st to 2nd order and count of total orders
pl <- ggplot(master_orders_diff_count, aes(x = diff, y = N)) + geom_point()


