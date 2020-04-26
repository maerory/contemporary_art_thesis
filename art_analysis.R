#Art data analysis
setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

library(xtable)
library(Matrix)
library(lme4)
library(numDeriv)
library(here)
library(dplyr)
source("algorithm3.R")
source("algorithm3BootInt.R")
source("auxFunctions.R")
source("intervalStr.R")
#source("algorithm3SE.R")
source("algorithm3SEWorking.R")

art = read.csv("art_sub.csv")
#Last row had no NAME
art = art[-length(art$NAME),]
#Change YOUNG to factor
art$YOUNG = as.factor(art$YOUNG)
#make a numeric ID vector
art = art %>% arrange(NAME)
art = art %>% mutate(ID = as.numeric(group_indices(.,NAME)))

#Make some plots
#For artists with at least 5 sales, is there any association between 
#variance of logrise and age?
temp = tabulate(art$ID)
ID5 = which(temp >= 2)
#Dataset containing only artists with at least 5 sales
art5 = art[which(art$ID %in% ID5),]
#Make a new data frame with columns for ID, YOUNG, and Var(logrise)
varlogrise = rep(0, length(unique(art5$ID)))
young = varlogrise
count = 1
for (i in unique(art5$ID)) {
  temp = art5[which(art5$ID == i),]
  young[count] = as.numeric(as.character(temp$YOUNG[1]))
  varlogrise[count] = var(temp$LOGRISE)
  count = count+1
}
#Make plot. Remember that 0 means dead, 1-5 is increasing in age.
plot(young, varlogrise)

##Skip ----------------------------------

#Change reference level to group of youngest artists
art$YOUNG = relevel(art$YOUNG, "1")

#create inputs for function
y = art$LOGRISE
id = art$ID
X = unname(model.matrix(~LOC+YOUNG, data = art))
U = unname(model.matrix(~1, data = art))
Z = unname(model.matrix(~YOUNG, data = art))
nIter = 10
nBoot = 100

#Model-based standard errors
artRes = algorithm3SE(y, X, U, Z, id, nIter, getSigmaSE = 1)
sigmaSE = artRes[[10]]
sigmaSE = sigmaSE[1]

#Bootstrap confidence intervals. Set seed for reproducibility. 
set.seed(1)
artResBoot = algorithm3BootInt(y, X, U, Z, id, nIter, nBoot, printN = FALSE)

#-------------------------------------------

#Try just on Art5
#Create ID
art5 = art5 %>% arrange(NAME)
art5 = art5 %>% mutate(ID = as.numeric(group_indices(.,NAME)))

#Change reference level to youngest artists
art5$YOUNG = relevel(art5$YOUNG, "1")

#create inputs for function
y = art5$LOGRISE
id = art5$ID
X = unname(model.matrix(~LOC+YOUNG, data = art5))
U = unname(model.matrix(~1, data = art5))
Z = unname(model.matrix(~YOUNG, data = art5))
nIter = 10
nBoot = 100

#Bootstrap confidence intervals
set.seed(1)
art5ResBoot = algorithm3BootInt(y, X, U, Z, id, nIter, nBoot, printN = FALSE)

#Model-based standard errors
art5Res = algorithm3SE(y, X, U, Z, id, nIter, getSigmaSE = 1)
sigma5SE = art5Res[[10]]
sigma5SE = sigma5SE[1]

