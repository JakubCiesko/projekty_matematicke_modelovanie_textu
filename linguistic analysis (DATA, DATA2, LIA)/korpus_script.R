path_to_written <- ..."PATH\\TO\\WRITTEN_CORPUS.csv"...
path_to_spoken <- ..."PATH\\TO\\SPOKEN_CORPUS.csv"...
written_corpus_size <- WRITTEN_CORPUS_SIZE
spoken_corpus_size <- SPOKEN_CORPUS_SIZE

compute_chisqtest <- function(row) {
  freqA <- as.numeric(row[2])
  freqB <- as.numeric(row[3])
  corpus_data <- data.frame(a = c(freqA, written_corpus_size - freqA), b = c(freqB, spoken_corpus_size  - freqB))
  chisq.test(corpus_data)
}

written_dataframe <- read.csv(path_to_written, header=FALSE, sep=";", dec=",")
spoken_dataframe <- read.csv(path_to_spoken, header=FALSE, sep=";", dec=",")
mixed_dataframe <- merge(written_dataframe, spoken_dataframe, by="V1")
shared_dataframe <- mixed_dataframe[,c("V1", "V2.x", "V2.y")]

results <- apply(shared_dataframe, MARGIN=1, FUN=compute_chisqtest) 