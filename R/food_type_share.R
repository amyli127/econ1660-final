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

# filter  2018 through oct 2020
pvd_orders <- pvd_orders[pvd_orders$year >= 2018,]
pvd_orders <- pvd_orders[!(pvd_orders$year == 2020 & pvd_orders$month == 11),]

# mex counts
mex_store_names <- c("Bajas Taqueria", "Bajas Tex Mex", "Caliente Mexican Grill")
mex_orders <- pvd_orders[pvd_orders$name %in% mex_store_names, ]
mex_orders_grouped <- mex_orders[, .N, by = .(year_month)]

# baj taq counts
baj_taq_orders <- pvd_orders[pvd_orders$name == "Bajas Taqueria", ]
baj_taq_orders_grouped <- baj_taq_orders[, .N, by = .(year_month)]

# baj tex counts
baj_tex_orders <- pvd_orders[pvd_orders$name == "Bajas Tex Mex", ]
baj_tex_orders_grouped <- baj_tex_orders[, .N, by = .(year_month)]

# cal counts
cal_orders <- pvd_orders[pvd_orders$name == "Caliente Mexican Grill", ]
cal_orders_grouped <- cal_orders[, .N, by = .(year_month)]
cal_orders_grouped <- rbind(cal_orders_grouped, list("01/18", 0))
cal_orders_grouped <- rbind(cal_orders_grouped, list("02/18", 0))
cal_orders_grouped <- rbind(cal_orders_grouped, list("03/18", 0))
cal_orders_grouped <- rbind(cal_orders_grouped, list("04/18", 0))
cal_orders_grouped <- rbind(cal_orders_grouped, list("05/18", 0))
cal_orders_grouped <- rbind(cal_orders_grouped, list("06/18", 0))
cal_orders_grouped <- rbind(cal_orders_grouped, list("07/18", 0))
cal_orders_grouped <- rbind(cal_orders_grouped, list("08/18", 0))
cal_orders_grouped <- rbind(cal_orders_grouped, list("09/18", 0))
cal_orders_grouped <- rbind(cal_orders_grouped, list("10/18", 0))
cal_orders_grouped <- rbind(cal_orders_grouped, list("11/18", 0))
cal_orders_grouped <- rbind(cal_orders_grouped, list("12/18", 0))
cal_orders_grouped <- rbind(cal_orders_grouped, list("01/19", 0))
cal_orders_grouped <- rbind(cal_orders_grouped, list("02/19", 0))
cal_orders_grouped <- rbind(cal_orders_grouped, list("03/19", 0))
cal_orders_grouped <- rbind(cal_orders_grouped, list("04/19", 0))


# all counts
all_orders_grouped <- pvd_orders[, .N, by = .(year_month)]

# shares
combined <- all_orders_grouped[mex_orders_grouped, on = .(year_month = year_month), nomatch = 0]
combined <- combined[baj_taq_orders_grouped, on = .(year_month = year_month), nomatch = 0]
combined <- combined[baj_tex_orders_grouped, on = .(year_month = year_month), nomatch = 0]
combined <- combined[cal_orders_grouped, on = .(year_month = year_month)]

combined[, mex_share := combined$i.N / combined$N]
combined[, baj_taq_share := combined$i.N.1 / combined$N]
combined[, baj_tex_share := combined$i.N.2 / combined$N]
combined[, cal_share := combined$i.N.3 / combined$N]


# graphing
combined$year_month <- factor(combined$year_month,
                                            levels = c("01/18", "02/18", "03/18", "04/18", "05/18", "06/18", "07/18", "08/18", "09/18", "10/18", "11/18", "12/18",
                                                       "01/19", "02/19", "03/19", "04/19", "05/19", "06/19", "07/19", "08/19", "09/19", "10/19", "11/19", "12/19",
                                                       "01/20", "02/20", "03/20", "04/20", "05/20", "06/20", "07/20", "08/20", "09/20", "10/20"))

combined_plot <- ggplot(combined, aes(x = year_month, group = 1)) +
      geom_line(aes(y = cal_share, color = "Caliente")) +
      geom_line(aes(y = mex_share, color = "All Mexican")) +
      geom_line(aes(y = baj_taq_share, color = "Bajas Taqueria")) +
      geom_line(aes(y = baj_tex_share, color = "Bajas Tex Mex")) +
      ggtitle("Mexican Restaurants' Shares of all Snackpass Orders in Providence") +
      ylab("% of all Snackpass Orders") +
      xlab("Month") +
      theme(axis.text.x = element_text(angle = 90, vjust = 0.5)) +
      geom_vline(xintercept = 17, linetype="dotted", color = "black", size=1.5) +
      scale_color_manual(values = c(
            'Caliente' = 'green',
            'All Mexican' = 'red',
            'Bajas Taqueria' = 'blue',
            'Bajas Tex Mex' = 'orange')) +
      labs(color = 'Restaurants', caption = "Data collected Jan 2018 - Oct 2020\nDotted line represents when Caliente opened")

plot(combined_plot)