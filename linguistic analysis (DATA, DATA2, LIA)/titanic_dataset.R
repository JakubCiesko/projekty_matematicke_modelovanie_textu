library(corrgram)
library(corrplot)
library(dendextend)
library(ggplot2)
library(class)
library(ltm)
library(dplyr)
library(dendextend)
library(ggdist)


add_legend <- function(...) {
  opar <- par(fig=c(0, 1, 0, 1), oma=c(0, 0, 0, 0), 
              mar=c(0, 0, 0, 0), new=TRUE)
  on.exit(par(opar))
  plot(0, 0, type='n', bty='n', xaxt='n', yaxt='n')
  legend(...)
}




# Načítanie dát
titanic_data <- read.table("D://kody//r//data//titanic.csv", 
                               header=T, 
                               dec=".", 
                               row.names=1, 
                               sep=",", 
                               fill=T)


# Predprocesing


# Určenie typov jednotlivých vlastností
head(titanic_data)
str(titanic_data)
variable_count <- ncol(titanic_data)
passenger_count <- nrow(titanic_data)

titanic_data_summary <- summary(titanic_data)


max(titanic_data$Age, na.rm=TRUE)
min(titanic_data$Age, na.rm=TRUE)

#Age histogram
hist(titanic_data$Age, col="#2d9999", main="Histogram vlastnosti Age", 
     xlab="Vek", ylab="Frekvencia")
#Age QQ-plot
qqnorm(titanic_data$Age, main="Normálny Q-Q graf", 
       xlab="Teoretické kvantily", 
       ylab="Vzorkové kvantily", col="#2d9999")
qqline(titanic_data$Age, lwd=2, col="red")
shapiro.test(titanic_data$Age)
ks.test(titanic_data$Age)


not_given_age_names <- titanic_data$Name[is.na(titanic_data$Age)]
original_mean_age <- mean(titanic_data$Age, na.rm=T)
#determining age of passengers with "Master" 
minor_indeces <- grepl("Master", titanic_data$Name, fixed = TRUE)
minor_age_summary <- summary(titanic_data$Age[minor_indeces])
# no_parch_children <- titanic_data$Parch[minor_indeces] == 0
minor_age_mean <- minor_age_summary["Mean"]
#setting age of minors to minor_age_mean
titanic_data[minor_indeces, ]$Age[is.na(titanic_data[minor_indeces, ]$Age)] <- minor_age_mean

#determining median age of passengers according to their titles
titanic_data$Title<-regmatches(as.character(titanic_data$Name),regexpr("\\,[A-z ]{1,20}\\.", as.character(titanic_data$Name)))
titanic_data$Title<-unlist(lapply(titanic_data$Title,FUN=function(x) substr(x, 3, nchar(x)-1)))
title_counts <- table(titanic_data$Title)
#Merging titles into groups
titanic_data$Title[which(titanic_data$Title %in% c("Mme", "Mlle"))] <- "Miss"
titanic_data$Title[which(titanic_data$Title %in% c("Lady", "Ms", "the Countess", "Dona"))] <- "Mrs"
titanic_data$Title[which(titanic_data$Title=="Dr" & titanic_data$Sex=="female")] <- "Mrs"
titanic_data$Title[which(titanic_data$Title=="Dr" & titanic_data$Sex=="male")] <- "Mr"
titanic_data$Title[which(titanic_data$Title %in% c("Capt", "Col", "Don", "Jonkheer", "Major", "Rev", "Sir"))] <- "Mr"
titanic_data$Title<-as.factor(titanic_data$Title) 
title.age <- aggregate(titanic_data$Age,by = list(titanic_data$Title), FUN = function(x) median(x, na.rm = T))
titanic_data[is.na(titanic_data$Age), "Age"] <- apply(titanic_data[is.na(titanic_data$Age), ],
                                                      1, function(x) title.age[title.age[, 1]==x["Title"], 2])
#median title age
median_title_age <- title.age
new_age_summary <- summary(titanic_data$Age)
new_age_summary["sd"] <-  sd(titanic_data$Age)

#deleting unused variables, mapping char variables onto int
new_data <- titanic_data[,c(-3,-8,-10,-12)]

sex.vector <- c(0,1)
names(sex.vector) <- c("male", "female")
new_data$Sex <-as.integer(sex.vector[new_data$Sex])



embarked.vector <- c(1,2,3,0)
names(embarked.vector) <- c("S", "C", "Q", "")
new_data$Embarked <-as.integer(embarked.vector[new_data$Embarked])



str(new_data)
new_data_summary <- summary(new_data)



# Analýza vlastností 



# Skúmanie binárnej premennej/vlastnosti - Survived
survived_counts <- table(titanic_data$Survived)
relative_survived_counts <- round(100*survived_counts/passenger_count,2)

survivors <- titanic_data[which(titanic_data$Survived==1),]
dead <-  titanic_data[which(titanic_data$Survived==0),]

#Pohlavie zivych
table(survivors$Sex)
sex_counts_survived <- round(100*table(survivors$Sex)/table(titanic_data$Sex),2)
sex_counts_survived <- round(100*table(survivors$Sex)/nrow(survivors),2)
#Pohlavie mrtvych
table(dead$Sex)
sex_counts_not_survived <- round(100*table(dead$Sex)/table(titanic_data$Sex),2)
sex_counts_not_survived <- round(100*table(dead$Sex)/nrow(dead),2)
#Pohlavie obecne
sex_table <- table(titanic_data$Sex)
relative_sex_counts <- round(100*sex_table/passenger_count,2)
survivor_sex_ratio_ratio <- round(survivor_sex_ratio/sex_ratio, 2)
dead_sex_ratio_ratio <- round(dead_sex_ratio/sex_ratio, 2)


survivor_sex_relationship <- chisq.test(titanic_data$Sex, titanic_data$Survived)
survivor_sex_relationship_statistic <- round(survivor_sex_relationship$statistic,2)
contrib <- 100*survivor_sex_relationship$residuals^2/survivor_sex_relationship$statistic
sex_contrib_rounded <- round(contrib, 3)
corrplot(contrib, is.cor = FALSE)


colnames(survivor_sex_relationship$residuals) <- c("Neprežil", "Prežil")
rownames(survivor_sex_relationship$residuals) <- c("Žena", "Muž")
corrplot(survivor_sex_relationship$residuals, 
         is.cor=F, 
         title="Vzťah medzi vlastnosťami Sex-Survived",mar=c(0,0,1,0))



survivor_pclass_relationship <- chisq.test(titanic_data$Pclass, titanic_data$Survived)
survivor_pclass_relationship_statistic <- round(survivor_pclass_relationship$statistic,2)

colnames(survivor_pclass_relationship$residuals) <- c("Neprežil", "Prežil")
rownames(survivor_pclass_relationship$residuals) <- c("1. trieda", "2. trieda", "3. trieda")
corrplot(survivor_pclass_relationship$residuals, 
         is.cor=F, 
         title="Vzťah medzi vlastnosťami Pclass-Survived",mar=c(0,0,1,0))


contrib <- 100*survivor_pclass_relationship$residuals^2/survivor_pclass_relationship$statistic
pclass_contrib_rounded <- round(contrib, 3)
corrplot(contrib, is.cor = FALSE, title="")



#Histogram Survived
myBreaks <- hist(titanic_data$Survived, plot=F)$breaks
myColors <- rep(c("#1b98e0","red"), length(myBreaks)/2) 

hist(titanic_data$Survived, 
     col=myColors,
     main="Histogram vlastnosti Survived",
     xlab="", ylab="Počet preživších", xaxt='n')



legendLabels <- c(paste("Obete (", survived_counts[1],")",sep=""), 
                  paste("Preživší ( ",survived_counts[2], ")",sep=""))

legend("topright",legendLabels, col=myColors, lwd=2)

#Histogram s farebnym rozlisenim podla pohlavia
ggplot(data=titanic_data, aes(x=Survived, fill = Sex)) + geom_histogram() + 
  ggtitle("Farebne rozdelený histogram vlastnosti Survived podľa pohlavia") + 
  xlab("0 - Neprežil 1 - Prežil") + ylab("Počet") +
  scale_fill_discrete(name = "Pohlavie", labels = c("Žena", "Muž"))

#Histogram s farebnym rozlisenm podla zakupenej triedy 
ggplot(data=titanic_data, aes(x=Survived,fill=as.factor(Pclass))) + geom_histogram() + 
  ggtitle("Farebne rozdelený histogram počtu preživších podľa zakúpenej triedy") + 
  xlab("0 - Neprežil 1 - Prežil") + ylab("Počet") + 
  scale_fill_discrete(name = "Zakúpená trieda", 
                      labels = c("1. trieda", "2. trieda", "3. trieda"))

ggplot(data=titanic_data, aes(x=Pclass,fill=as.factor(Survived))) + geom_histogram() + 
  ggtitle("Farebne rozdelený histogram počtu cestujúcich v jednotlivých triedach") + 
  xlab("Trieda") + ylab("Počet") + 
  scale_fill_discrete(name = "Vlastnosť Survived:", 
                      labels = c("0 - Neprežil", "1 - Prežil"))


third_class_sur_ratio <- round(100*table(new_data$Survived[new_data$Pclass == 3]) / sum(table(new_data$Survived[new_data$Pclass == 3])),2)
second_class_sur_ratio <- round(100*table(new_data$Survived[new_data$Pclass == 2]) / sum(table(new_data$Survived[new_data$Pclass == 2])),2)
first_class_sur_ratio <- round(100*table(new_data$Survived[new_data$Pclass == 1]) / sum(table(new_data$Survived[new_data$Pclass == 1])),2)

third_class_sur_table <- table(new_data$Survived[new_data$Pclass == 3])
second_class_sur_table <- table(new_data$Survived[new_data$Pclass == 2])
first_class_sur_table <- table(new_data$Survived[new_data$Pclass == 1])



class_ratio <- round(100*table(titanic_data$Pclass)/nrow(titanic_data),2)
survivors_class_ratio <- round(100*table(survivors$Pclass)/nrow(survivors),2)
dead_class_ratio <- round(100*table(dead$Pclass)/nrow(dead),2)


dead_ratio_change_ratio <- round(dead_class_ratio/class_ratio * 100, 2)
# 62.50% z toho co malo umriet 1. trieda
# 85.71% z toho co malo umriet 2. trieda
# 123.64% z toho co malo umriet 3. trieda
survivor_ratio_change_ratio <- round(survivors_class_ratio/class_ratio * 100,2)
# 166.67% z toho co malo prezit 1. trieda
# 119.05% z toho co malo prezit 2. trieda
# 63.64% z toho co malo prezit 3. trieda


#Grafy
p <- ggplot(new_data, aes(x=Survived, y=SibSp, color=as.factor(Survived))) + 
  geom_violin(trim=FALSE, draw_quantiles = c(0.25, 0.5, 0.75)) + 
  ggtitle("Violinplot vlastnosti SibSp dvoch skupín\nvytvorených na základe hodnoty vlastnosti Survived") + 
  xlab("Survived") + ylab("Počet súrodencov/partnerov")  + labs(color = "Hodnota vlastnosti \nSurvived:")


p  + stat_summary(fun.data="mean_sdl",
                 geom="crossbar", width=0.5 ) + coord_flip()


ggplot(data=titanic_data, aes(x=Age,fill = as.factor(Survived))) + geom_histogram() + 
  ggtitle("Farebne rozdelený histogram vekových kategórií podľa prežitia") + 
  xlab("Vek") + ylab("Počet") + 
  scale_fill_discrete(name = "Prežil", labels = c("Nie", "Áno"))



ggplot(data=titanic_data, aes(x=Age,fill = as.factor(Embarked))) + geom_histogram() + 
  ggtitle("Farebne rozdelený histogram vekových kategórií podľa prežitia") + 
  xlab("Vek") + ylab("Počet")


#Boxploty
cont_data <- new_data[c(-1,-2,-3,-8)]
boxplot(scale(cont_data), col="#1b98e0", 
        main="Krabicový graf vlastností:\n Age, SibSp, Parch, Fare")
boxplot(scale(cont_data[c(-2,-3)]), col="#1b98e0", 
        main="Krabicový graf vlastností: Age, Fare")


#Vlastnosti tych co su v triedach
first_class_age <- round(summary(new_data$Age[new_data$Pclass == 1]),2)
second_class_age <- round(summary(new_data$Age[new_data$Pclass == 2]),2)
third_class_age <- round(summary(new_data$Age[new_data$Pclass == 3]),2)
survived_age_rounded <- round(summary(new_data$Age[new_data$Survived == 1]),2)
dead_age_rounded <- round(summary(new_data$Age[new_data$Survived == 0]),2)

age_shapiro_statistic <- round(shapiro.test(titanic_data$Age)$statistic,2)


#Fare
fare_summary_rounded <- round(summary((titanic_data$Fare)),2)

hist(titanic_data$Fare, breaks=20,col="#2d9999", 
     main="Histogram vlastnosti Fare", 
     xlab="Cena lístka", 
     ylab="Frekvencia intervalu ceny")

#Parch
survivor_parch_summary <- summary(survivors$Parch)
dead_parch_summary <- summary(dead$Parch)
#SibSp
survivor_sibsp_summary <- summary(survivors$SibSp)
dead_sibsp_summary <- summary(dead$SibSp)






mylogit <- glm(Survived ~ Age + Sex + Pclass,
               data=new_data, family="binomial")



predictions <- predict(mylogit, newdata=new_data, type = "res")





cm <- table(round(predictions), new_data$Survived)
logit_confussion_matrix <- cm
accuracy <- sum(cm[1], cm[4]) / sum(cm[1:4])
precision <- cm[4] / sum(cm[4], cm[2])
sensitivity <- cm[4] / sum(cm[4], cm[3])
fscore <- (2 * (sensitivity * precision))/(sensitivity + precision)
specificity <- cm[1] / sum(cm[1], cm[2])

# Informácie o logistickej regresii
logit_summary <- summary(mylogit)
logit_confint <- confint(mylogit)




ggplot(new_data, aes(x=Fare + Age, y=Survived)) + geom_point() +
  stat_smooth(method="glm", color="green", se=T,
              method.args = list(family=binomial)) +
  ggtitle("Logistická regresia:\nSurvived ~ Age + Sex + Pclass") + 
  xlab("Age + Sex + Pclass") + ylab("Survived")





#Analyza entit

#data without Survived
new_new_data <- new_data[c(-1)]
#pairwise distance matrix
pdm <- dist(scale(new_new_data), method="can")
cl <- hclust(pdm, method="ave")



bcdendro <- as.dendrogram(cl) %>% 
  color_labels(k=2)%>%
  color_branches(k=2)%>%
  set("branches_lwd", c(1.5,1.5,1.5))


clustersMembership <- cutree(bcdendro, k=2)
cluster_membership_colors <- clustersMembership
cluster_membership_colors[which(cluster_membership_colors==2)] <- "#1b98e0" 
cluster_membership_colors[which(cluster_membership_colors==1)] <- "#e01b36"


survived_colors <- titanic_data$Survived
survived_colors[which(survived_colors==1)] <- "#1b98e0" 
survived_colors[which(survived_colors==0)] <- "#e01b36"


my_mds <- cmdscale(pdm,eig=TRUE, k=2)
mds_gof <- round(my_mds$GOF,2)

x <- my_mds$points[,1]
y <- my_mds$points[,2]
plot(x, y, xlab="MDS súradnica 1", ylab="MDS súradnica 2",
     main="MDS", col=survived_colors)
legend("topright", legend=c("Prežil", "Neprežil"),
       col=c("#1b98e0", "#e01b36"), cex=0.8, lty=1, lw=3)


par(mfrow = c(2,1))
par(mar=c(4.1, 4.1, 4.1, 4.1), xpd=TRUE)
plot(x, y, xlab="MDS súradnica 1", ylab="MDS súradnica 2",
     main="MDS", col=survived_colors)
plot(x, y, xlab="MDS súradnica 1", ylab="MDS súradnica 2",
     main="Príslušnosť ku clusterom", col=cluster_membership_colors)
add_legend("topright", legend=c("Prežil/Cluster 2", "Neprežil/Cluster 1"), pch=20, 
           col=c("#1b98e0", "#e01b36"),
           horiz=TRUE, bty='n', cex=0.8)

par(mfrow = c(1,1))



pca_summary <- summary(myPCA)
plot(x,y, col=survived_colors, main="PCA\nKomponenta 1 = 0,33xPclass - 0,41xSex + 0,10xAge - 0,43xSibSp - 0,51xParch - 0,53xFare\nKomponenta 2 = 0,59xPclass - 0,56xAge + 0,37xSibSp + 0,29xParch - 0,35xFare", 
     xlab="Komponenta 1",
     ylab="Komponenta 2")

legend("topright", legend=c("Prežil", "Neprežil"),
       col=c("#1b98e0", "#e01b36"), cex=0.8, lty=1, lw=3)

biplot(myPCA)







new_data %>% 
  filter(Pclass %in% c(1, 2, 3)) %>% 
  ggplot(aes(x = factor(Pclass), y = Age, fill = factor(Pclass))) +
  
  # add half-violin from {ggdist} package
  stat_halfeye(
    # adjust bandwidth
    adjust = 0.5,
    # move to the right
    justification = -0.2,
    # remove the slub interval
    .width = 0,
    point_colour = NA
  ) +
  geom_boxplot(
    width = 0.12,
    # removing outliers
    outlier.color = NA,
    alpha = 0.5
  ) +
  gghalves::geom_half_point(
    ## draw jitter on the left
    side = "l", 
    ## control range of jitter
    range_scale = .4, 
    ## add some transparency
    alpha = .3
  ) + ggtitle("Graf frekvencie hodnôt vlastnosti Age v jednotlivých triedach") +
  xlab("Trieda - Pclass") + ylab("Vek") + labs(fill = "Trieda") +  
  coord_flip() 


titanic_data %>% 
  filter(Embarked %in% c("S", "Q")) %>% 
  ggplot(aes(x = factor(Pclass), y = Age, fill = factor(Pclass))) +
  
  # add half-violin from {ggdist} package
  stat_halfeye(
    # adjust bandwidth
    adjust = 0.6,
    # move to the right
    justification = -0.2,
    # remove the slub interval
    .width = 0,
    point_colour = NA
  ) +
  geom_boxplot(
    width = 0.12,
    # removing outliers
    outlier.color = NA,
    alpha = 0.5
  ) +
  gghalves::geom_half_point(
    ## draw jitter on the left
    side = "l", 
    ## control range of jitter
    range_scale = .4, 
    ## add some transparency
    alpha = .3
  ) + coord_flip()






titanic_data[titanic_data$Fare < 400,] %>% 
  filter(Survived %in% c(0,1)) %>% 
  ggplot(aes(x = factor(Survived), y = Fare, fill = factor(Survived))) +
  
  # add half-violin from {ggdist} package
  stat_halfeye(
    # adjust bandwidth
    adjust = 0.6,
    # move to the right
    justification = -0.05,
    # remove the slub interval
    .width = 0.2,
    point_colour = NA
  ) +
  geom_boxplot(
    width = 0.14,
    # removing outliers
    outlier.color = NA,
    alpha = 0.5
  ) +
  gghalves::geom_half_point(
    ## draw jitter on the left
    side = "l", 
    ## control range of jitter
    range_scale = .3, 
    ## add some transparency
    alpha = .4
  ) +  ggtitle("Graf frekvencie hodnôt vlastnosti Fare rozdelenej do dvoch skupín podľa Survived") +
  xlab("Hodnota vlastnosti Survived") + ylab("Fare") + labs(fill = "Prežil:") + coord_flip()
