# 1. zlty slide (20/127)
# Načtěme do R knihu Švejk a zjistěme, jakou má průměrnou délku slov.

source("https://raw.githubusercontent.com/oltkkol/vmod/master/simplest_text.R")
svejkText <- GetFileContent("PATH")
svejkTokens <- TokenizeText(svejkText)
svejkTokenLens <- nchar(svejkTokens)
svejkTokenLensInfo <- summary(svejkTokenLens)
svejkAvgTokenLen <- svejkTokenLensInfo[["Mean"]]
# svejkAvgTokenLen = 4.845669 char/word

# 2. zlty slide (21/127)
# Jaká je průměrná délka slov typů („slovníku“)
svejkTypes <- unique(svejkTokens)
svejkTypesLens <- nchar(svejkTypes)
svejkTypesLensInfo <- summary(svejkTypesLens)
svejkAvgTypesLen <- svejkTypesLensInfo[["Mean"]]
# svejkAvgTypesLen = 7.423909 char/word

# 3. zlty slide (23/127) & 4. zlty slide (28/127)
# Pro dostatečně dlouhý text vyrobme graf, jak se mění průměrná délka slov, když text roste.

dataToPlot <- list(x=c(),y=c())
max_text_len <- 10**4
for (n in 1:max_text_len) {
  if (!n %% 1000){print(n)}
  firstNAvgTokenLen <- mean(svejkTokenLens[1:n])
  dataToPlot[["x"]] <- append(dataToPlot[["x"]], n)
  dataToPlot[["y"]] <- append(dataToPlot[["y"]], firstNAvgTokenLen)
}
plot(log(dataToPlot$x), dataToPlot$y, 
     type="l", 
     xlab="Log Text length",
     ylab="Average Token Length")

# predchadzajuci quest s pouzitim sample

dataToPlot <- list(x=c(),y=c())
max_text_len <- 10**4
for (n in 1:max_text_len) {
  if (!n %% 1000){print(n)}
  firstNAvgTokenLen <- mean(sample(svejkTokenLens,n,replace=T))
  dataToPlot[["x"]] <- append(dataToPlot[["x"]], n)
  dataToPlot[["y"]] <- append(dataToPlot[["y"]], firstNAvgTokenLen)
}
plot(log(dataToPlot$x), dataToPlot$y, 
     type="l", 
     xlab="Log Text length",
     ylab="Average Token Length")


# 4. zlty slide (slide 44/127)
# Udělejte odhad průměrné délky slov pro autora z jediné jeho knihy

avgTokenLen <- c()
nSample <- 1000
totalIterationNumber <- 1000
for (i in 1:totalIterationNumber) {
  myTokenLenSample <- sample(svejkTokenLens, nSample, replace=T)
  avgTokenLenInSample <- mean(myTokenLenSample)
  avgTokenLen <- append(avgTokenLen, avgTokenLenInSample)}
par(mfrow=c(2,1))
percentiles <- qnorm(c(0.0275, 0.975), mean(avgTokenLen), sd(avgTokenLen))
hist(avgTokenLen)
abline(v=c(mean(avgTokenLen), percentiles[1], percentiles[2]), col="red", lwd=2)
plot(avgTokenLen, xlab="Sample index",type="l")
abline(h=c(mean(avgTokenLen), percentiles[1], percentiles[2]), col="red", lwd=2)
par(mfrow=c(1,1))

# iny sposob:
avgTokenLen <- bootstrap(svejkTokenLens,nSample,
                         totalIterationNumber=totalIterationNumber,
                         fn = mean)


# 5. zlty slide (53/127)
# Udělejme odhad průměrné délky slov pro italštinu a pro němčinu (viz. uloha predtym)
bootstrap <- function(data, sampleSize, 
                      totalIterationNumber=1000, fn=NULL, 
                      diff=F, splitSamples=F){
  #Creates two types of empty results
  #depending on given splitSamples bool
  result <- c()
  if (splitSamples){
    result <- list()
  }
  #Bootstrap cycle
  for (i in 1:totalIterationNumber){
    if (!diff){
        dataSample <- sample(data, sampleSize, replace=T)
      
    if (!is.null(fn)){
      result <- append(result, fn(dataSample))
    }
    else
      {
      if (splitSamples) {
          result[[i]] <- dataSample}
      else {
        result <- append(result, dataSample)}
      }
    }
  else {
    dataSample1 <- sample(data[[1]], sampleSize, replace=T)
    dataSample2 <- sample(data[[2]], sampleSize, replace=T)
    result <- append(result, mean(dataSample1)-mean(dataSample2))
    }}
  return(result)
}


compareTwoLanguages <- function(langOneTokens, langTwoTokens, sampleSize, totalIterationNumber=1000){
  #compares average word length in two languages
  lengthLimit <- min(length(langOneTokens), length(langTwoTokens))
  if (sampleSize > lengthLimit) {sampleSize <- lengthLimit}
  langOneTokenLens <- nchar(langOneTokens)[1:lengthLimit]
  langTwoTokenLens <- nchar(langTwoTokens)[1:lengthLimit]
  langData <- list(lang1=langOneTokenLens,lang2=langTwoTokenLens)
  results <- bootstrap(langData, sampleSize, totalIterationNumber, diff=T)
  return(results)
}     

#bootstrap rozdielu dlzok dvoch textov v anglictine a cestine
rslt <- compareTwoLanguages(tokens_in_folder$`Composing Questions (Hadas Kotek) (z-lib.org).txt`, 
                            tokens_in_folder$`bezruc slezske pisne.txt`, 2000, 
                            totalIterationNumber=100)
hist(rslt)
#ziaden z intervalov (bins) histogramu neobsahuje 0:
#priemerna dlzka slov v anglictine a cestine nie je rovnaka (je odlisna)


# 6. zlty slide (58/127)
# Využívá italština odlišnou průměrnou délku slov než němčina, angličtina? (viz uloha predtym)
# Je v češtině „y“ používáno více než „i“? 

drawHist <- function(data, qntlAblines=F){
    hist(data)
    if(qntlAblines){
      qntls <- qnorm(c(0.025,0.975), mean(data),sd(data))
      abline(v=qntls[1],col="red",lwd=2)
      abline(v=qntls[2],col="red",lwd=2)
      abline(v=mean(data),col="blue",lwd=2)
    }
  }

getFreq <- function(lst, querryElement){
  #returns querried element freq in lst
  return (length(which(lst==querryElement)))
} 

compareFrequency <- function(plain_text, let1,let2, n){
  #compares frequency of two letters (let1, let2) in plain_text
  matches <- TokenizeText(plain_text, paste("[",let1,let2,"]"), T)
  result <- c()
  for (i in 1:n){
    resampled <- sample(matches, replace = T)
    result <- append(result, getFreq(resampled,let1)/length(resampled)-getFreq(resampled,let2)/length(resampled))}
  return (result)
}

rslt <- compareFrequency(svejkText, 'i', 'y', 120)
drawHist(rslt, T)
# histogram neobsahuje 0 -> i a y maju rozdielnu frekvenciu


# 7. zlty slide (63/127)
# pravdepodobnost n lavakov vo vagone regiojetu

population <- c(rep('p',90),rep('l',10))
lefties <- c()
for (i in 1:1000){
  vagon <- sample(population, 5,replace=T)
  lefties <- append(lefties,length(which(vagon=='l')))
}

twoOrMoreLeftiesProb <- length(which(lefties>=2))
nLeftiesProbability <- prop.table(table(lefties))
barplot(nLeftiesProbability)
prop.table(table(lefties))


#Odhad hodnoty pravdepodobnosti s vyuzitim, ze ak n (pocet pokusov) n-> inf,
#tak relativna frekvencia javu konverguje k jeho pravdepodobnosti
guessProbability <- function(threshold, n = 100, plotBool=T){
  result <- c()
  probabilites <- c()
  for (j in 1:n) {
    for (i in 1:n){
      preresult <- which(sample(c('l','p'), 5, replace=T, prob = c(0.1,0.9)) =='l')
      if (length(preresult)==threshold){
        result <- append(result, 1)
      }
      if (length(preresult)!=threshold){
        result <- append(result, 0)
      }
      
    }
    probabilites <- append(probabilites, length(which(result==1))/length(result))}
  if (plotBool) {
    plot(probabilites)}
  return (probabilites)}


getAndPlotSimulatedProbabilities <- function(lowerBound,upperBound, 
                              plotDimX, plotDimY, 
                              n=100, plotBool=T){
  if (plotBool) {par(mfrow=c(plotDimX,plotDimY))}
  results <- list()
  for(i in lowerBound:upperBound) {
    results[[as.character(i)]] <-  mean(guessProbability(i, n, plotBool))
  }
  par(mfrow=c(1,1))
  return (results)
}

getAndPlotSimulatedProbabilities(0, 3, 2, 2, n=200)
nLeftiesProbability
# lefties
# 0     1     2     3 
# 0.578 0.340 0.067 0.015 

# 8. zlty slide (108/127)
# Vytvořte odhad využívání jednotlivých grafémů pro Italštinu,zobrazte boxplotem.

italianTokens <- TokenizeText(GetFileContent("PATH"))
someItalianTokens <- italianTokens[1:length(italianTokens)/2]
# Urcenie talianskych grafemov
# 1. sposob
italianAlphabet <- unique(strsplit(paste(someItalianTokens,collapse=""),"")[[1]])
italianAlphabet
# "i" "m" "e" "n" "t" "r" "l" "c" "o" "a" "s" "d" "v" "p" "g"
# "ě" "b" "h" "u" "ŕ" "ů" "q" "f" "_" "z" "ň" "č" "w" "y" "ç"
# "1" "8" "6" "2" "0" "5" "î" "x" "k" "é" "7" "j" "ę" "ô"
# 2. sposob
italianAlphabet <- strsplit("eaionlrtscdupmvghfbqzàèéìòùykwxjô","")

italianTokensSamples <- bootstrap(italianTokens,2500,totalIterationNumber=2000,splitSamples = T)

#alphabetWord <- paste(italianTokensSamples[1:15], collapse="")
#italianAlphabet <- unique(strsplit(alphabetWord, "")[[1]])

lettersFreqs <- list()
for (tokenSample in italianTokensSamples){
  randomLongWord <- tolower(paste(tokenSample, collapse=""))
  lettersTable <- prop.table(table(strsplit(randomLongWord, "")[[1]]))
  for (i in 1:length(lettersTable)){
    letter <- names(lettersTable)[i]
    if (letter %in% italianAlphabet[[1]]){
    lettersFreqs[[letter]] <- append(lettersFreqs[[letter]], lettersTable[[letter]])
    }
  }
}

boxplot(lettersFreqs, main="Probability of Italian Graphemes")


italianGraphemesFreq <- sapply(lettersFreqs,summary)
write.table(as.table(italianGraphemesFreq),file="PATH", sep="\t")

#   "a"	"b"	"c"	"d"	"e"	"f"	"g"	"h"	"i"	"l"	"m"	"n"	"o"	"p"	"q"	"r"	"s"	"t"	"u"	"v"	"x"	"z"	"é"	"w"	"k"	"y"	"j"	"ô"
# "Min."  0.115828179842888	0.0071227430843134	0.00147637795275591	0.0307200786434013	0.000755287009063444	0.00805699262149097	0.0141485598787266	0.00826998579901428	0.0855697504930121	0.0598333333333333	0.0208934941396297	0.00190887210556893	0.0851224421335122	0.0230395084904855	0.00300200133422282	0.00083153168135706	0.0456079690458549	0.0485436893203883	0.000728508984944148	0.0202121439906456	8.02825947334618e-05	0.00401371352119742	8.02825947334618e-05	8.04052424218059e-05	8.04052424218059e-05	8.03987779385753e-05	8.03987779385753e-05	8.05607024893257e-05
# "1st Qu."	0.122692665508046	0.0100864575511351	0.043006993313748	0.0348308528989365	0.110347402522525	0.0104408110558591	0.0173802119304533	0.0107628646913927	0.0913726745985314	0.0666708284778869	0.0249456058271353	0.0664908517676499	0.0913785954752821	0.0267915049738148	0.00465839205744268	0.0637625031893411	0.0506714751033195	0.055763008371044	0.0295141422315993	0.0241373562842655	8.36120401337793e-05	0.00605893935316267	8.29582928253799e-05	8.26514587982478e-05	8.28981182127166e-05	8.2771179500714e-05	8.27746047512623e-05	8.25832633437735e-05
# "Median"	0.124615381168193	0.0107720588526443	0.044377848825329	0.0359398178225555	0.112249114261084	0.011174815050635	0.0182244754872892	0.0113945844278355	0.0930742134805589	0.0683668388170171	0.0260004921181622	0.0680821120772687	0.0929535232383808	0.0277905954477304	0.0051389564107218	0.0650771617420227	0.0520798471331414	0.0572821965704257	0.0305981710396173	0.0251535585527769	0.000166666666666667	0.00663514988813641	8.38609586781974e-05	8.33402783565297e-05	8.36785073219132e-05	8.34411115808423e-05	8.32431532506451e-05	8.31981376575018e-05
# "Mean"	0.124553762601872	0.01081600180575	0.0430055282760427	0.0359666756997635	0.110992458527812	0.0111865141664547	0.0182608686732604	0.0113990671481735	0.093073071131292	0.0684621325008619	0.0259846903250386	0.0663466233494757	0.0929853494769625	0.0277997509890934	0.00513013998967589	0.0642200116310132	0.0520511221651445	0.0573195609428858	0.0295080440500033	0.0251905848812994	0.000189586482019101	0.00665898200598261	0.000115907815236605	8.83959306987457e-05	0.000114284399878449	9.38792899127297e-05	8.99743035778417e-05	8.54434469501282e-05
# "3rd Qu."	0.126435102903797	0.0115230460921844	0.0456643866498537	0.037065479557647	0.113978580343428	0.0118857941690817	0.0191462263182603	0.0120389790722965	0.0947642405079808	0.0702778733028076	0.0269844232131661	0.069706839061941	0.0945793431472561	0.0288891696543399	0.00556993409439638	0.0665291811168086	0.0534402315950935	0.0589511001685829	0.0316823052124383	0.0262376163159792	0.000250375563345017	0.00721518673745596	0.00016508120965099	8.40724706181046e-05	0.000165207335205683	8.4226485130252e-05	8.3994793656212e-05	8.40565701830196e-05
# "Max."	0.133476678795898	0.0147009966777409	0.051228654727197	0.042174320524836	0.121897686982948	0.0157676348547718	0.0228782287822878	0.0143963630240781	0.102146065546498	0.0775476387738194	0.0316326530612245	0.0759127705270114	0.101330008312552	0.0332400855685371	0.00768010685366057	0.0723280861640431	0.0581237253569001	0.0650912106135987	0.0355218855218855	0.0303436714165968	0.000917431192660551	0.01	0.000411319512997697	0.000246751110379997	0.000421300977418268	0.000252334090335604	0.000170401295049842	0.000169520257670792


# 9. zlty slide (120/127)
# 1) Vyberte z textu náhodně jedno (lemmata):
#   adjektivum, podstatné jméno, sloveso, spojku, sloveso
# sample(x, 1)
# 
# 2) Zjistěte průměrnou délku vět vybraného textu


library(udpipe)
downloadInfo <- udpipe_download_model(language="czech")
downloadInfo
svejkChapter <- GetFileContent("PATH")
model <- udpipe_load_model("PATH")
annotation <- udpipe_annotate(model, x=svejkChapter)
annotationTable <- as.data.frame(annotation)
pos <- annotationTable$upos
nounsLemmas <- annotationTable[which(pos=="NOUN"),"lemma"]
adjsLemmas <- annotationTable[which(pos=="ADJ"),"lemma"]
verbsLemmas <- annotationTable[which(pos=="VERB"),"lemma"]
conjLemmas <- annotationTable[which(pos=="CCONJ"),"lemma"]

random <- function(data){
  return(sample(data, size=1))
}
# Náhodne vybrané substantívum, adjektívum, sloveso, spojka
randomNoun <- random(nounsLemmas)
randomAdj <- random(adjsLemmas) 
randomVerb <- random(verbsLemmas)
randomConj <- random(conjLemmas)
c(randomNoun, randomAdj,randomVerb,randomConj)
# "účastník"  "promokavý" "prodávat"  "a"

# priemerna dlzka viet x' v danom texte
sentenceLens <- as.vector(table(annotationTable$sentence_id))
senLenSummary <- summary(sentenceLens)
avgSenLen <- as.numeric(senLenSummary["Mean"])
avgSenLen
# avgSenLen = 19.30751 word/sent



# 10. zlty slide (122/127)
#
# 1) Získejte z textu všechna podstatná jména ve 3. pádu
# … užijte „xpos“
# 
# 2) Které pády podst. jmen jsou nejčastější? 
#   … užijte substr(…), sloupec xpos, samplování a boxplot


# vsetky podstatne mena v 3. pade (dativ)
nouns <- annotationTable[which(annotationTable$upos=="NOUN"),]
dativeNouns <- nouns[grepl("Case=Dat", nouns$feats),"token"]
dativeNouns



# najcastejsie pady podstatnych mien
cases <- list(N=c(),G=c(),
              D=c(),A=c(),
              L=c(),V=c(), 
              I=c(), NotGiven=c())
pattern <- "Case=\\K\\w"
nounSamples <- bootstrap(nouns$feats,200,splitSamples=T)
nounSamplesXpos <- bootstrap(nouns$xpos, 200, splitSamples=T)
for (nounSample in nounSamples){
  thisSampleCaseCount <- list()
  for (noun in nounSample){
    case <- regmatches(noun, regexpr(pattern,noun,perl=T))
    if (length(case)>0){
        if (case %in% names(thisSampleCaseCount)){
          thisSampleCaseCount[[case]] <- thisSampleCaseCount[[case]] + 1}
        else {
          thisSampleCaseCount[[case]] <- 1
        }
    }
    else {
        if ("NotGiven" %in% names(thisSampleCaseCount)){
          thisSampleCaseCount[["NotGiven"]] <- thisSampleCaseCount[["NotGiven"]] + 1 
        }
        else {thisSampleCaseCount[["NotGiven"]] <- 1}
    }
  }
  for (index in 1:length(thisSampleCaseCount)){
    case <- names(thisSampleCaseCount)[index]
    caseCount <- thisSampleCaseCount[[case]]
    cases[[case]] <- append(cases[[case]], caseCount)
  }
}

sapply(cases, summary)
# Absolutna frekvencia jednotlivych padov substantiv
# N        G         D        A        L        V        I NotGiven
# Min.    35.00000 24.00000  2.000000 30.00000  5.00000 1.000000  5.00000 1.000000
# 1st Qu. 48.00000 37.00000  7.000000 48.00000 20.00000 2.000000 14.00000 1.000000
# Median  52.00000 41.00000 10.000000 53.00000 22.00000 3.000000 17.00000 2.000000
# Mean    51.97795 40.95627  9.643146 52.64425 22.65417 3.502273 16.97207 2.164626
# 3rd Qu. 56.00000 45.00000 12.000000 57.00000 26.00000 5.000000 20.00000 3.000000
# Max.    74.00000 62.00000 21.000000 77.00000 37.00000 9.000000 30.00000 7.000000


getRelativeFreq <- function(n, sampleSize){
  return(n/sampleSize)
}
getRelativeFreq200Ss <- function(n){
  return(getRelativeFreq(n, 200))
}

relativeCases <- sapply(cases, getRelativeFreq200Ss)
boxplot(cases, main="Noun Cases Frequency")
boxplot(relativeCases, main="Noun Cases Probability")
sapply(relativeCases, summary)
# Relativna frekvencia jednotlivych padov substantiv
# sapply(relativeCases, summary)
# N         G          D         A         L          V          I   NotGiven
# Min.    0.1750000 0.1200000 0.01000000 0.1500000 0.0250000 0.00500000 0.02500000 0.00500000
# 1st Qu. 0.2400000 0.1850000 0.03500000 0.2400000 0.1000000 0.01000000 0.07000000 0.00500000
# Median  0.2600000 0.2050000 0.05000000 0.2650000 0.1100000 0.01500000 0.08500000 0.01000000
# Mean    0.2598897 0.2047813 0.04821573 0.2632212 0.1132709 0.01751136 0.08486035 0.01082313
# 3rd Qu. 0.2800000 0.2250000 0.06000000 0.2850000 0.1300000 0.02500000 0.10000000 0.01500000
# Max.    0.3700000 0.3100000 0.10500000 0.3850000 0.1850000 0.04500000 0.15000000 0.03500000

#To iste s pouzitim funkcie substr
cases <- list("1"=c(),"2"=c(),
              "3"=c(),"4"=c(),
              "5"=c(),"6"=c(), 
              "7"=c())


for (nounSample in nounSamplesXpos){
  thisSampleCaseCount <- list()
  for (noun in nounSample){
    case <- substr(noun, 5,5)
    if (length(case)>0){
      if (case %in% names(thisSampleCaseCount)){
        thisSampleCaseCount[[case]] <- thisSampleCaseCount[[case]] + 1}
      else {
        thisSampleCaseCount[[case]] <- 1
      }
    }
    else {
      if ("NotGiven" %in% names(thisSampleCaseCount)){
        thisSampleCaseCount[["NotGiven"]] <- thisSampleCaseCount[["NotGiven"]] + 1 
      }
      else {thisSampleCaseCount[["NotGiven"]] <- 1}
    }
  }
  for (index in 1:length(thisSampleCaseCount)){
    case <- names(thisSampleCaseCount)[index]
    caseCount <- thisSampleCaseCount[[case]]
    cases[[case]] <- append(cases[[case]], caseCount)
  }
}




# 11. zlty slide (126/127)
# finalny quest
# Vytvořte skript, který …
# pro zadaný adresář načte všechny texty a získá:
# * počet tokenů
# * počet typů
# * průměrnou délku slov
# * průměrnou délku vět (udpipe!)
# * celkový počet sloves (udpipe!)
# * celkový počet podstatných jmen ve 2. pádu (udpipe!)
# * vypočítá entropii slov:
#   table( tokeny) / length( tokeny ) -> p
# 
# - sum( p * log(p) ) -> vyslednaEntropie
# 
# 
# A sám výsledky pro jednotlivé texty uloží jako řádky v tabulce s popsanými sloupci.

textsInFolder <- GetFilesContentsFromFolder("PATH")
tokensInFolder <- TokenizeTexts(textsInFolder)

getNumberOfTypes <- function(tokens){
  return(length(unique(tokens)))
  
}

getMeanWordLen <- function(words){
  return(mean(nchar(words)))
}
# pocet tokenov v textovych suboroch v zlozke
numberOfTokensInFolder <- sapply(tokensInFolder, length)
numberOfTokensInFolder
# pocet tokenov:
# svejk_01.txt svejk_02.txt svejk_03.txt 
# 326          308          468 

# pocet typov v textovych suboroch v zlozke
numberOfTypesInFolder <- sapply(tokensInFolder, getNumberOfTypes)
numberOfTypesInFolder
# pocet typov:
# svejk_01.txt svejk_02.txt svejk_03.txt 
# 220          220          324 

# priemerna dlzka slov 
meanWordLens <- sapply(tokensInFolder, getMeanWordLen)
meanWordLens
#priemerna dlzka slov:
# svejk_01.txt svejk_02.txt svejk_03.txt 
# 4.889571     5.155844     5.083333 

library(udpipe)
annotate <- function(plainText, returnDataFrame=T) {
  # !!uses model from outter scope!!
  result <- udpipe_annotate(model, x=plainText)
  if (returnDataFrame){
    result <- as.data.frame(result) 
  }
  return(result)
}



# priemerna dlzka viet

meanSentLen <- function(textAnnotation){
  return(mean(table(textAnnotation["sentence_id"])))
}

folderAnnotationTable <- sapply(textsInFolder, annotate)
transposedFolderAnnotationTable <- t(folderAnnotationTable)
apply(transposedFolderAnnotationTable, 1, meanSentLen)
# priemerna dlzka viet: 
# svejk_01.txt svejk_02.txt svejk_03.txt 
# 15.77778     21.33333     21.92857

# celkovy pocet slovies

getPOSCount <- function(textAnnotation, POS){
  POScount <- table(textAnnotation[["upos"]] == POS)
  if ("TRUE" %in% names(POScount)){
    return(POScount[["TRUE"]])}
  else {
    return(0)
  }
}

getVerbCount <- function(textAnnotation){
  return(getPOSCount(textAnnotation, POS="VERB"))
}


apply(transposedFolderAnnotationTable, 1, getVerbCount)
# Pocet slovies
# svejk_01.txt svejk_02.txt svejk_03.txt 
# 47           36           79 


# celkovy pocet podstatnych mien v 2. pade (G)

getNounsInGenitive <- function(transposedFolderAnnotationTable){
  pattern <- "Case=\\K\\w"
  row.names(transposedFolderAnnotationTable)
  "NOUN" == substr(noun,1,4)
  genitiveNouns <- list()
  for (i in 1:length(row.names(transposedFolderAnnotationTable))){
    textAnnotation <- transposedFolderAnnotationTable[i,]
    tokensInfo <- paste(textAnnotation[["upos"]], textAnnotation[["feats"]])
    for (j in 1:length(tokensInfo)){
      tokenInfo <- tokensInfo[j]
      if (substr(tokenInfo, 1, 4) == "NOUN"){
        case <- regmatches(tokenInfo, regexpr(pattern,tokenInfo,perl=T))
        if (!identical(case, character(0))){
          if (case == "G"){
            token <- textAnnotation[["token"]][j]
            genitiveNouns[[row.names(transposedfolderAnnotationTable)[i]]] <- append(genitiveNouns[[row.names(transposedfolderAnnotationTable)[i]]], token)
          }
        }
      }
      
    }
  }
  return(genitiveNouns)
  
}
genitiveNounsInFolder <-  getNounsInGenitive(transposedFolderAnnotationTable)


# entropia slov 

getTokensProbability <- function(tokens){
  return(table(tokens)/length(tokens))
}
calculateEntropy <- function(probability){
  return(-sum(probability*log(probability)))
}

tokensProbability <- sapply(tokensInFolder, getTokensProbability)
tokensEntropy <- sapply(tokensProbability, calculateEntropy)
tokensEntropy
# svejk_01.txt svejk_02.txt svejk_03.txt 
# 5.134813     5.197470     5.552506 


