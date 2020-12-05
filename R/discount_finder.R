library(data.table)
library(ggplot2)

# read in data
# master_orders <- fread('data/bigfiles/master_orders.txt')
# pvd_stores <- fread('data/smallfiles/pvd_stores.txt')
# datetime <- fread('data/bigfiles/datetime.txt')
# 
# setnames(pvd_stores, "_id", "id")
# pvd_orders <- master_orders[pvd_stores, on = .(store = id), nomatch = 0]
# pvd_orders <- pvd_orders[datetime, on = .(createdAt = createdAt), nomatch = 0]
# pvd_orders[, date_hour := paste(pvd_orders$date, pvd_orders$hour, sep="-")]
# pvd_orders[, week := strftime(createdAt, "%V")]

# two hours, group on in_school
pvd_activity_grouped <- pvd_orders[, .N, by = .(name, week, day_of_week, hour, year)]
pvd_activity_stats <- pvd_activity_grouped[, .(avg = mean(N), std = sd(N)), by = .(name, day_of_week, hour, year)]
pvd_activity_stats[, upper := avg + 4 * std]

pvd_orders_grouped_counts <- pvd_orders[, .N, by = .(name, week, day_of_week, hour, year)]

pvd_orders_combined <- pvd_orders_grouped_counts[pvd_activity_stats , on = .(name = name, day_of_week = day_of_week, hour = hour, year = year)]
pvd_orders_combined <- pvd_orders_combined[, discount := N > upper]
pvd_orders_combined[, in_school := (week >= 4 & week <= 19) | (week >= 37 & week <= 51)]

pvd_discounts <- pvd_orders_combined[discount == TRUE & in_school == TRUE]
